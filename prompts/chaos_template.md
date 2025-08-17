# Nightwalker CHAOS Daily Brief – {{timestamp}}

## Executive Summary
- **Top Signals:** {{top_signals}}
- **Narrative Shifts (Pulse):** {{pulse_summary}}
- **Confidence:** {{confidence_summary}}

---
{% for item in items %}
## {{loop.index}}. {{item.title}}
**Link:** {{item.link}}  
**Published:** {{item.published}}  
**Source:** {{item.source}}

**Summary:** {{item.summary}}

**Thinker:** {{item.thinker}}  
**Doer:** {{item.doer}}  
**Controller:** {{item.controller}}  
**Pulse:** {{item.pulse}}

**Entities:** {{item.entities}}

**Truth Vector:** `{{item.truth_vector}}`

---
{% endfor %}

{% if entity_co_occurrences %}
## Top Entity Co-occurrences
{{ entity_co_occurrences }}

{% endif %}
## Method Notes
- Truth Vector dimensions: Empirical, Logical, Emotional, Historical.
- Requires analyst validation.
- 
{% if ai_analysis %}
## AI Analysis
{{ ai_analysis }}
{% endif %}
