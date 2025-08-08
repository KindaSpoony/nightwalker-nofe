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

**Truth Vector:** `{{item.truth_vector}}`

---
{% endfor %}

## Method Notes
- Truth Vector: Empirical, Logical, Emotional, Historical dimensions.
- Requires analyst validation.
