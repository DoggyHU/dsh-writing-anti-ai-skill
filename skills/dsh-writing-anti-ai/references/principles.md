# Principles — Why Each Pattern Signals AI

Understanding *why* a pattern is AI-generated is essential for handling edge cases. This file explains the mechanism behind each pattern category so the agent can judge whether a given instance is genuinely AI writing or legitimate usage.

---

## 1. Filler Phrases (填充词)

**Mechanism**: LLMs are trained to be helpful, polite, and thorough. They pad sentences with "值得注意的是" and "需要强调的是" because these phrases appear frequently in training data as discourse markers. Humans skip them.

**Why it's detectable**: Real human writing gets to the point. Filler phrases are a statistical signature of the "helpful assistant" training objective.

**Edge case**: In formal diplomatic or legal texts, some cautious framing may be intentional. Distinguish structural filler from deliberate hedging.

---

## 2. Value-Judgment Adjectives (价值判断形容词)

**Mechanism**: LLMs default to positive, affirming language. "重要的", "完善的", "著名的", "优良的" are safe, generic praise words that the model uses when it has no specific information to convey.

**Why it's detectable**: Humans use value judgments sparingly and only when they mean something specific. AI sprinkles them everywhere as filler.

**Rule of thumb**: If removing the adjective doesn't change the factual claim, it's AI filler. "建立了完善的质控体系" and "建立了质控体系" convey the same fact — one just sounds like a press release.

---

## 3. Vague Attributions (模糊归因)

**Mechanism**: LLMs hallucinate authority. "专家认为" and "研究表明" are safe ways to sound credible without naming anyone. The model doesn't actually know who said what.

**Why it's detectable**: Real academic and technical writing cites specific sources. Vague attributions are the signature of a system that generates plausible-sounding prose without real sourcing.

**Hard rule**: If you can't name the expert or the study, delete the attribution. "专家认为该政策有效" → either cite the expert or just say "该政策在[具体方面]产生了效果".

---

## 4. Mechanical Enumeration (机械枚举)

**Mechanism**: LLMs learned from textbooks and how-to articles that enumerate steps with "首先...其次...第三...最后". This structure is so common in training data that models reproduce it reflexively for any sequential description.

**Why it's detectable**: Humans writing about real processes don't mechanically number every step. Some steps get a paragraph, others a sentence. The uniformity itself is the fingerprint.

**How to fix**: Collapse some steps into phrases, expand others into full paragraphs. Break the 1-2-3-4-5 rhythm.

---

## 5. Self-Praising Conclusions (自我表扬式总结)

**Mechanism**: LLMs are trained to produce "satisfying" completions. A paragraph that ends with "为...奠定了坚实基础" or "有效保障了...科学性、准确性和可靠性" is the model's attempt at a satisfying wrap-up.

**Why it's detectable**: Real technical writing doesn't praise itself. It states results and moves on. Self-praise paragraphs are a genre marker of government propaganda, which is heavily represented in Chinese LLM training data.

**Hard rule**: If a concluding sentence could be appended to any report in the same domain without changing its meaning, delete it.

---

## 6. Double Modifiers (双重修饰)

**Mechanism**: LLMs hedge by pairing synonyms. "验证与确认", "精密度与准确度", "科学性与可靠性" — the model is essentially saying the same thing twice because it's uncertain which word is right.

**Why it's detectable**: Humans pick one word. AI picks both to be safe. This is a direct consequence of the model optimizing for coverage rather than precision.

**Fix**: Keep the more specific term. Delete the other. "精密度与准确度" → "精密度" (if that's what was actually measured) or "准确度" (if that's the real metric).

---

## 7. AI Vocabulary (AI高频词)

**Mechanism**: Certain words are overrepresented in LLM outputs because of training data biases. "依托" appears far more often in AI-generated Chinese than in human writing. "赋能", "闭环", "抓手" are buzzwords from Chinese tech/business media that LLMs absorbed and overuse.

**Why it's detectable**: These are statistical outliers. A human might use "依托" once in 5000 characters. AI uses it once every 500.

**Fix**: Replace with plain alternatives. "依托平台" → "通过平台". "赋能产业" → "支持产业发展" or just describe what actually happens.

---

## 8. Encyclopedia Openings (百科式开头)

**Mechanism**: LLMs are heavily trained on Wikipedia and Baidu Baike. When asked to write about a place, organization, or topic, the model defaults to the encyclopedia entry pattern: "XX位于...是...的重要...".

**Why it's detectable**: This is a genre mismatch. Technical reports and papers don't need encyclopedia-style introductions. The reader already knows what the report is about.

**Fix**: Start with what the reader actually needs. For a report chapter, that's usually the specific topic of the chapter, not geographic background.

---

## 9. 了-Stacking (了字堆砌)

**Mechanism**: Chinese LLMs overuse 了 as a completion marker. Every action "完成了", "实现了", "形成了", "建立了", "确保了" — the cumulative effect is a rhythmic drone.

**Why it's detectable**: Human Chinese writing varies aspect marking. Not every verb needs 了. AI uses it as a default sentence-ending pattern.

**Fix**: Remove 了 where the completion is already implied by context. Alternate with other structures (是...的, 着, or plain statements).

---

## 10. Policy Slogans (政策口号残余)

**Mechanism**: Chinese LLMs are heavily exposed to government documents. Phrases like "严守耕地保护红线", "全面推进乡村振兴", "促进高质量发展" are memorized templates that the model inserts whenever the topic is even tangentially related.

**Why it's detectable**: These phrases belong to a specific genre (government work reports). Their presence in technical reports, academic papers, or narrative writing is a genre contamination.

**Fix**: Translate slogans into factual statements. "严守耕地保护红线" → "保护耕地面积不减少". "全面推进乡村振兴" → state what specific measures were taken.
