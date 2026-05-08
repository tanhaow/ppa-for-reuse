"""Custom widgets for Django Admin."""

import json
from django import forms
from django.utils.safestring import mark_safe


class AdapterFieldSelectorWidget(forms.Widget):
    """
    Custom widget for selecting adapter fields with a visual interface.
    Provides a user-friendly way to configure list_view_fields without
    manually writing JSON.
    """

    template_name = "admin/widgets/adapter_field_selector.html"

    class Media:
        css = {"all": ("admin/css/adapter_field_selector.css",)}
        js = ("admin/js/adapter_field_selector.js",)

    def __init__(self, attrs=None, adapter_name=None):
        super().__init__(attrs)
        self.adapter_name = adapter_name

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        # Parse current value
        if value:
            try:
                if isinstance(value, str):
                    fields = json.loads(value)
                else:
                    fields = value
            except (json.JSONDecodeError, TypeError):
                fields = []
        else:
            fields = []

        # Get available fields from adapter
        available_fields = self._get_available_fields()

        context["widget"].update(
            {
                "current_fields": fields,
                "available_fields": available_fields,
                "adapter_name": self.adapter_name,
            }
        )

        return context

    def _get_available_fields(self):
        """Get available fields from the adapter."""
        if not self.adapter_name:
            return []

        try:
            from ppa.adapters.loader import get_adapter

            adapter = get_adapter(self.adapter_name)

            if not adapter or not adapter.field_map:
                return []

            # Build list of available fields
            fields = []
            for field_name in adapter.field_map.keys():
                # Create a friendly label from field name
                label = field_name.replace("_", " ").title()
                fields.append({"name": field_name, "label": label, "suggested_label": label})

            return fields
        except Exception:
            return []

    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget."""
        self.get_context(name, value, attrs)

        # Parse current value for JSON representation
        if value:
            try:
                if isinstance(value, str):
                    fields = json.loads(value)
                else:
                    fields = value
            except (json.JSONDecodeError, TypeError):
                fields = []
        else:
            fields = []

        # Get available fields
        available_fields = self._get_available_fields()

        html = f"""
        <div class="adapter-field-selector" data-name="{name}">
            <div class="field-selector-header">
                <h3>Select Fields to Display</h3>
                <button type="button" class="add-field-btn">+ Add Field</button>
            </div>

            <div class="selected-fields" id="selected-fields-{name}">
                <!-- Selected fields will be rendered here -->
            </div>

            <div class="available-fields" style="display: none;">
                <h4>Available Fields</h4>
                <select class="available-fields-select" id="available-fields-{name}">
                    <option value="">-- Select a field --</option>
                    {self._render_field_options(available_fields)}
                </select>
            </div>

            <!-- Hidden input to store JSON value -->
            <input type="hidden" name="{name}" id="id_{name}" value='{json.dumps(fields)}' />

            <div class="json-preview">
                <details>
                    <summary>JSON Preview</summary>
                    <pre id="json-preview-{name}">{json.dumps(fields, indent=2)}</pre>
                </details>
            </div>
        </div>

        <script>
        (function() {{
            const container = document.querySelector('.adapter-field-selector[data-name="{name}"]');
            const hiddenInput = document.getElementById('id_{name}');
            const selectedFieldsContainer = document.getElementById('selected-fields-{name}');
            const jsonPreview = document.getElementById('json-preview-{name}');
            const addFieldBtn = container.querySelector('.add-field-btn');
            const availableFieldsSelect = document.getElementById('available-fields-{name}');

            let fields = {json.dumps(fields)};

            function renderFields() {{
                selectedFieldsContainer.innerHTML = '';

                if (fields.length === 0) {{
                    selectedFieldsContainer.innerHTML = '<p class="no-fields">No fields selected. Click "Add Field" to add fields.</p>';
                    return;
                }}

                fields.forEach((field, index) => {{
                    const fieldDiv = document.createElement('div');
                    fieldDiv.className = 'field-item';
                    fieldDiv.innerHTML = `
                        <div class="field-item-header">
                            <span class="field-order">${{index + 1}}</span>
                            <span class="field-name">${{field.field}}</span>
                            <div class="field-actions">
                                <button type="button" class="move-up" data-index="${{index}}" ${{index === 0 ? 'disabled' : ''}}>↑</button>
                                <button type="button" class="move-down" data-index="${{index}}" ${{index === fields.length - 1 ? 'disabled' : ''}}>↓</button>
                                <button type="button" class="remove" data-index="${{index}}">×</button>
                            </div>
                        </div>
                        <div class="field-item-body">
                            <label>
                                Field Name:
                                <input type="text" class="field-name-input" data-index="${{index}}" value="${{field.field}}" readonly />
                            </label>
                            <label>
                                Display Label:
                                <input type="text" class="field-label-input" data-index="${{index}}" value="${{field.label}}" />
                            </label>
                        </div>
                    `;
                    selectedFieldsContainer.appendChild(fieldDiv);
                }});

                updateJSON();
            }}

            function updateJSON() {{
                hiddenInput.value = JSON.stringify(fields);
                jsonPreview.textContent = JSON.stringify(fields, null, 2);
            }}

            function addField(fieldName, fieldLabel) {{
                fields.push({{
                    field: fieldName,
                    label: fieldLabel
                }});
                renderFields();
            }}

            function removeField(index) {{
                fields.splice(index, 1);
                renderFields();
            }}

            function moveField(index, direction) {{
                const newIndex = index + direction;
                if (newIndex < 0 || newIndex >= fields.length) return;

                [fields[index], fields[newIndex]] = [fields[newIndex], fields[index]];
                renderFields();
            }}

            function updateFieldLabel(index, newLabel) {{
                fields[index].label = newLabel;
                updateJSON();
            }}

            // Event listeners
            addFieldBtn.addEventListener('click', () => {{
                const fieldName = prompt('Enter field name (e.g., cookbook_cook_time):');
                if (!fieldName) return;

                const fieldLabel = prompt('Enter display label:', fieldName.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase()));
                if (!fieldLabel) return;

                addField(fieldName, fieldLabel);
            }});

            selectedFieldsContainer.addEventListener('click', (e) => {{
                const target = e.target;
                const index = parseInt(target.dataset.index);

                if (target.classList.contains('remove')) {{
                    if (confirm('Remove this field?')) {{
                        removeField(index);
                    }}
                }} else if (target.classList.contains('move-up')) {{
                    moveField(index, -1);
                }} else if (target.classList.contains('move-down')) {{
                    moveField(index, 1);
                }}
            }});

            selectedFieldsContainer.addEventListener('input', (e) => {{
                if (e.target.classList.contains('field-label-input')) {{
                    const index = parseInt(e.target.dataset.index);
                    updateFieldLabel(index, e.target.value);
                }}
            }});

            // Initial render
            renderFields();
        }})();
        </script>

        <style>
        .adapter-field-selector {{
            border: 1px solid #ddd;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 4px;
        }}

        .field-selector-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}

        .field-selector-header h3 {{
            margin: 0;
            font-size: 14px;
            font-weight: 600;
        }}

        .add-field-btn {{
            background: #417690;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
        }}

        .add-field-btn:hover {{
            background: #2e5266;
        }}

        .selected-fields {{
            min-height: 50px;
        }}

        .no-fields {{
            color: #666;
            font-style: italic;
            text-align: center;
            padding: 20px;
        }}

        .field-item {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 10px;
            padding: 10px;
        }}

        .field-item-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}

        .field-order {{
            background: #417690;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }}

        .field-name {{
            flex: 1;
            font-family: monospace;
            font-weight: 600;
        }}

        .field-actions {{
            display: flex;
            gap: 5px;
        }}

        .field-actions button {{
            background: #f0f0f0;
            border: 1px solid #ddd;
            padding: 4px 8px;
            cursor: pointer;
            border-radius: 3px;
            font-size: 14px;
        }}

        .field-actions button:hover {{
            background: #e0e0e0;
        }}

        .field-actions button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .field-actions .remove {{
            background: #dc3545;
            color: white;
            border-color: #dc3545;
        }}

        .field-actions .remove:hover {{
            background: #c82333;
        }}

        .field-item-body {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}

        .field-item-body label {{
            display: block;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 4px;
        }}

        .field-item-body input {{
            width: 100%;
            padding: 6px;
            border: 1px solid #ddd;
            border-radius: 3px;
            font-size: 13px;
        }}

        .field-item-body input[readonly] {{
            background: #f5f5f5;
            color: #666;
        }}

        .json-preview {{
            margin-top: 15px;
        }}

        .json-preview summary {{
            cursor: pointer;
            font-weight: 600;
            padding: 8px;
            background: #e9ecef;
            border-radius: 4px;
        }}

        .json-preview pre {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
            overflow-x: auto;
            margin-top: 10px;
        }}
        </style>
        """

        return mark_safe(html)

    def _render_field_options(self, fields):
        """Render option elements for available fields."""
        options = []
        for field in fields:
            options.append(
                f'<option value="{field["name"]}" data-label="{field["suggested_label"]}">'
                f'{field["label"]}</option>'
            )
        return "\n".join(options)

    def value_from_datadict(self, data, files, name):
        """Extract value from form data."""
        value = data.get(name)
        if value:
            try:
                # Validate JSON
                parsed = json.loads(value)
                return parsed
            except json.JSONDecodeError:
                return value
        return None
