#!/usr/bin/env python3
"""Test cache performance"""

from core.ai_service import AIService
import time

print('='*80)
print('🔥 CACHE PERFORMANCE TEST')
print('='*80)

service = AIService()

# Test same questions again - should be cached
questions = [
    'MTS PDRN คืออะไรคะ',
    'มีโปรโมชั่นอะไรบ้างคะ',
    'คลินิกอยู่ที่ไหนคะ',
]

print(f'\n📊 Initial Cache Stats:')
stats = service.get_cache_stats()
for key, val in stats.items():
    print(f'   • {key}: {val}')

print('\n' + '='*80)
print('Testing cached responses (should be < 50ms each):')
print('='*80)

for i, q in enumerate(questions, 1):
    start = time.time()
    response = service.chat_completion(
        [
            {'role': 'system', 'content': service.get_system_prompt()},
            {'role': 'user', 'content': q}
        ],
        stream=False,
        use_cache=True
    )
    latency = (time.time() - start) * 1000
    answer = ''.join(response)
    
    print(f'\n{i}. {q}')
    print(f'   ⏱️  Latency: {latency:.2f}ms')
    print(f'   📏 Length: {len(answer)} chars')
    if latency < 50:
        print(f'   ✅ CACHED!')
    else:
        print(f'   ⚠️  NOT CACHED (new request)')

print('\n' + '='*80)
print('📊 Final Cache Stats:')
print('='*80)
stats = service.get_cache_stats()
for key, val in stats.items():
    print(f'   • {key}: {val}')

print(f'\n🎯 Cache Hit Rate: {stats["hit_rate_percent"]}%')
if stats["hit_rate_percent"] > 80:
    print('✅ Excellent cache performance!')
elif stats["hit_rate_percent"] > 50:
    print('✓ Good cache performance')
else:
    print('⚠️  Cache needs more data')

print('='*80)
