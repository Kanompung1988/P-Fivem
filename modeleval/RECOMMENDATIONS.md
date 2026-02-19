# 💡 Recommendations & Best Practices

**Strategic recommendations for maximizing AI chatbot performance**

---

## 🎯 Model Selection Strategy

### Scenario 1: Standard Deployment (Recommended)

**Primary Model:** Typhoon-v2.5-30B  
**Prompt:** v6_fewshot (with examples)  
**Caching:** Enabled (1-hour TTL)  
**RAG:** Enabled

**Why:**
- Best quality for Thai language (80%)
- Native Thai understanding
- Reasonable cost ($0.15/1k)
- 100% success rate

**Expected Performance:**
- Quality: 80%
- Latency: 6-7 seconds
- Monthly cost (50k queries): ~$7.50

---

### Scenario 2: Speed-Optimized

**Primary Model:** DeepSeek-v3  
**Prompt:** v1_professional  
**Caching:** Enabled (1-hour TTL)  
**RAG:** Enabled

**Why:**
- Fast response (4.3s vs 6.7s)
- Same quality as Typhoon (80%)
- Good for real-time chat

**Trade-offs:**
- 60% more expensive ($0.24/1k vs $0.15/1k)
- Not Thai-optimized

---

### Scenario 3: Cost-Optimized

**Smart Routing:**
- Simple queries → GPT-4o-mini ($0.09/1k)
- Complex queries → Typhoon-v2.5-30B ($0.15/1k)

**Implementation:**
```python
def classify_complexity(query):
    simple_keywords = ["ราคา", "เท่าไหร่", "จองคิว", "เวลา", "ที่อยู่", "เบอร์"]
    return any(kw in query.lower() for kw in simple_keywords)

if classify_complexity(user_query):
    model = "gpt-4o-mini"  # Cheap
else:
    model = "typhoon-v2.5-30b"  # Quality
```

**Expected Savings:** 40-50% cost reduction

---

## 🔧 Prompt Optimization

### Recommended Prompt by Use Case

| Use Case | Recommended Prompt | Reason |
|----------|-------------------|--------|
| General Chatbot | v6_fewshot | Consistent format, includes examples |
| LINE Bot | v2_friendly | Conversational tone |
| Website FAQ | v3_concise | Quick, direct answers |
| Medical Compliance | v4_safety | Emphasizes safety |
| Sales Campaign | v5_sales | Conversion-focused |
| API Integration | v7_structured | JSON output |

### Custom Prompt Tips

1. **Include Examples:** Models perform better with 3-5 examples
2. **Clear Guidelines:** Explicit dos and don'ts
3. **Thai Context:** Mention this is for Thai customers
4. **Safety First:** Always mention not to diagnose medical conditions
5. **Call-to-Action:** Guide user to next steps

---

## 📊 RAG (Retrieval-Augmented Generation) Strategy

### What to Include in RAG Knowledge Base

**High Priority:**
1. **Services & Pricing** (most queries ~73%)
   - Complete service list with prices
   - Package deals
   - Treatment duration & frequency

2. **Promotions** (40% error rate - needs improvement)
   - Current active promotions
   - Terms & conditions
   - Expiry dates

3. **Clinic Information** (35% error rate)
   - Hours, location, contact
   - Staff qualifications
   - Booking process

**Medium Priority:**
4. Before/after care instructions
5. Safety information & contraindications
6. Common FAQs

### RAG Best Practices

```python
# Example: Enhanced RAG query

def get_rag_context(user_query):
    # 1. Retrieve top 3 relevant documents
    docs = rag_service.retrieve(user_query, top_k=3)
    
    # 2. Format context clearly
    context = "ข้อมูลจากฐานความรู้:\n\n"
    for i, doc in enumerate(docs, 1):
        context += f"{i}. {doc['title']}\n{doc['content']}\n\n"
    
    # 3. Include metadata
    context += f"(อ้างอิง: {len(docs)} เอกสาร, ความเชื่อมั่น: {docs[0]['score']:.2f})"
    
    return context
```

### Update Frequency

- **Daily:** Promotions, pricing changes
- **Weekly:** Service updates, blog content
- **Monthly:** General information, policies

---

## 🚀 Performance Optimization

### 1. Caching Strategy

**What to Cache:**
- Identical queries → 100% hit rate
- FAQ-style questions
- Popular queries (top 20%)

**Cache Configuration:**
```python
cache_config = {
    "ttl": 3600,  # 1 hour for most
    "ttl_promotions": 86400,  # 24 hours for promotions
    "ttl_pricing": 3600,  # 1 hour for pricing (changes often)
    "max_size": 1000,  # Store top 1000 queries
}
```

**Expected Impact:** 50-70% cost reduction

### 2. Response Time Optimization

**Current Latency:**
- Typhoon: 6.7s
- DeepSeek: 4.3s
- GPT-4o: 2.2s

**Optimization Tactics:**

1. **Streaming Responses** (Advanced)
```python
response = client.chat.completions.create(
    model="typhoon-v2.5-30b",
    messages=[...],
    stream=True  # Stream chunks as they arrive
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="")
```

2. **Parallel Processing**
```python
# If multiple queries at once
import asyncio

async def process_batch(queries):
    tasks = [get_response_async(q) for q in queries]
    return await asyncio.gather(*tasks)
```

3. **Reduce max_tokens**
```python
# 800 tokens = ~600 Thai words (plenty for most answers)
max_tokens=800  # Current
max_tokens=600  # Faster, cheaper
```

### 3. Cost Optimization

**Monthly Cost Breakdown (100k queries):**

| Component | Baseline | With Optimization | Savings |
|-----------|----------|-------------------|---------|
| AI API | $15.00 | $7.50 (caching) | 50% |
| Compute | $2.00 | $2.00 | 0% |
| **Total** | **$17.00** | **$9.50** | **44%** |

**Advanced: Smart Routing**
- 60% simple → GPT-4o-mini ($0.09/1k)
- 40% complex → Typhoon ($0.15/1k)
- **New total:** $11.40 (33% savings vs optimized)

---

## 📈 Quality Improvement Plan

### Phase 1: Quick Wins (Week 1-2)

1. **Switch to v6_fewshot prompt** → +5-10% quality
2. **Add category-specific examples** → Fix promotions/clinic_info errors
3. **Improve RAG** → Better context = better answers

### Phase 2: Data Collection (Week 3-4)

1. **Log all queries & responses**
2. **Collect user feedback** (👍/👎)
3. **Human evaluation** (use templates provided)

### Phase 3: Iterative Improvement (Ongoing)

1. **Weekly review** of low-rated responses
2. **Update knowledge base** based on common questions
3. **A/B test** different prompts
4. **Fine-tune** (if volume > 10k labeled pairs)

---

## 🔍 Monitoring & Alerts

### Key Metrics to Track

1. **Response Quality**
   - User feedback (thumbs up/down)
   - Escalation rate (% forwarded to human)
   - Keyword match score

2. **Performance**
   - Average latency (target: < 5s)
   - 95th percentile latency (target: < 10s)
   - Error rate (target: < 2%)

3. **Cost**
   - Daily spend
   - Cost per query
   - Cache hit rate

### Alert Thresholds

```yaml
alerts:
  latency_p95:
    threshold: 15000  # ms
    action: "Switch to DeepSeek or investigate"
  
  error_rate:
    threshold: 0.05  # 5%
    action: "Check API status, review logs"
  
  cost_daily:
    threshold: 10  # USD
    action: "Review query volume, check for abuse"
  
  cache_hit_rate:
    threshold: 0.3  # 30%
    action: "Review caching strategy"
```

---

## 🛡️ Safety & Compliance

### Input Validation

```python
# core/input_guard.py

blocklist = [
    # Harmful content
    "ช่วยฆ่า", "วิธีทำร้าย",
    
    # Off-topic
    "คริปโตเคอเรนซี่", "หวย", "การเมือง",
    
    # Competitor mentions (optional)
    # "คลินิก[คู่แข่ง]"
]

def is_safe(query: str) -> bool:
    query_lower = query.lower()
    return not any(blocked in query_lower for blocked in blocklist)
```

### Output Validation

**Red Flags to Monitor:**
- Medical diagnosis ("คุณเป็นโรค...")
- Guaranteed results ("ได้ผล 100%...")
- Competitor comparison ("ดีกว่า [คลินิก X]...")
- Pricing promises ("ถูกที่สุด...")

**Solution:** Post-processing filter

```python
def validate_response(response: str) -> str:
    red_flags = ["คุณเป็นโรค", "ได้ผล 100%", "ถูกที่สุด"]
    
    if any(flag in response for flag in red_flags):
        return fallback_response()
    
    return response
```

---

## 🎓 Training Deployment Team

### Knowledge Transfer Checklist

- [ ] **Benchmark Results Review** (30 min)
  - Understand model comparison
  - Review error patterns
  - Discuss recommendations

- [ ] **Technical Walkthrough** (1 hour)
  - Code architecture
  - Integration points
  - API configuration

- [ ] **Hands-on Testing** (1 hour)
  - Run local tests
  - Test with sample queries
  - Review logs/monitoring

- [ ] **Deployment Planning** (30 min)
  - Timeline
  - Rollback plan
  - Escalation path

---

## 🚨 Incident Response

### Common Issues & Solutions

#### Issue 1: High Latency (> 10s)

**Symptoms:** Users complaining about slow responses

**Diagnosis:**
```bash
# Check recent latency
grep "latency_ms" logs/ai_queries.jsonl | tail -100 | jq '.latency_ms' | stats
```

**Solutions:**
1. Switch to DeepSeek (faster)
2. Reduce max_tokens (800 → 600)
3. Enable caching if not already
4. Check API status page

#### Issue 2: High Error Rate (> 5%)

**Symptoms:** Many failed API calls

**Diagnosis:**
```bash
# Check error types
grep "error" logs/ai_queries.jsonl | tail -50
```

**Solutions:**
1. Verify API key validity
2. Check API rate limits
3. Enable fallback model
4. Contact API provider

#### Issue 3: Poor Quality Responses

**Symptoms:** Users unhappy with answers

**Diagnosis:**
```bash
# Run error analysis
python modeleval/error_analysis.py logs/recent_queries.json
```

**Solutions:**
1. Review & update prompt
2. Improve RAG context
3. Add more examples
4. Consider human-in-the-loop

---

## 📅 Recommended Roadmap

### Week 1-2: Launch MVP
- Integrate Typhoon with v6_fewshot prompt
- Enable caching + RAG
- Deploy to beta users (10-20 people)
- Monitor closely

### Week 3-4: Optimize
- Collect feedback
- Run human evaluation
- Fine-tune prompt based on errors
- Expand to more users (100-200)

### Month 2: Scale
- Full production launch
- Implement smart routing
- Set up automated monitoring
- Weekly performance reviews

### Month 3+: Improve
- A/B test prompts
- Consider fine-tuning
- Expand knowledge base
- Reduce cost further

---

## 🎯 Success Metrics

### Goals (3 Months)

| Metric | Target | Measurement |
|--------|--------|-------------|
| User Satisfaction | > 4.0/5.0 | 👍👎 rating |
| Response Quality | > 85% | Human eval |
| Average Latency | < 5s | Logs |
| Error Rate | < 2% | Logs |
| Cost per Query | < $0.001 | API bills |
| Cache Hit Rate | > 50% | Cache stats |

### Review Cadence

- **Daily:** Error rate, latency, cost
- **Weekly:** Quality review, user feedback
- **Monthly:** Full performance report, optimization planning

---

## 🤝 Support Resources

### Documentation
- `MODEL_HANDOFF.md` - Complete handoff
- `INTEGRATION_GUIDE.md` - Technical integration
- `README.md` - Project overview
- `API_KEYS_GUIDE.md` - API setup

### Scripts
- `error_analysis.py` - Analyze performance
- `generate_human_eval.py` - Create evaluation templates
- `test_prompts.py` - Test prompt versions
- `benchmark_real_data.py` - Re-run benchmarks

### Data
- `results/benchmark_*.json` - Benchmark results
- `results/low_quality_responses_for_review.csv` - Problem cases
- `results/human_evaluation_template.csv` - Evaluation template
- `data/` - Knowledge base

---

## ✨ Future Enhancements

### Short-term (3-6 months)
- [ ] Multi-turn conversation support
- [ ] Image understanding (skin analysis)
- [ ] Voice input/output
- [ ] Personalized recommendations

### Long-term (6-12 months)
- [ ] Fine-tuned custom model
- [ ] Proactive engagement (follow-ups)
- [ ] Multi-language support (English, Chinese)
- [ ] Appointment scheduling integration

---

**Document Version:** 1.0  
**Last Updated:** February 19, 2026  
**Prepared By:** AI Engineering Team
