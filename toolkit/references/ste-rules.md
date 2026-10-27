# ASD-STE100 writing rules — working summary

This is a working summary in our own words of ASD-STE100 **Issue 9** (released
15 January 2025; 53 writing rules; became an international standard with the
subtitle "Standard for Technical Documentation"). It is not a copy of the
standard. The official standard and its dictionary are free on request from
https://www.asd-ste100.org.

Mode for this skill: **strict STE, technical nouns and technical verbs of the
topic allowed**. Every technical noun/verb that is not general vocabulary goes
in the page glossary with a one-sentence STE definition.

---

## 1. Words

| Rule | What to do |
|---|---|
| Approved words | Use words from the STE dictionary in their approved meaning and approved part of speech only. One word = one meaning (e.g. "follow" = come after, not "obey"; "right" = the side, not "correct"). |
| Technical nouns (Issue 9 term, was "technical names") | Allowed when they name a thing in the subject field: parts, tools, materials, processes, units, software names, people roles, life forms, laws. Use the same name every time. Do not use synonyms. |
| Technical verbs (terms) | Allowed only for the small set of subject-specific actions with no approved verb (e.g. *compile*, *ream*, *machine*, *drill*). Use them as verbs, not as general words. |
| -ing forms | Use only as part of a technical noun ("landing gear", "cooling fan") or as a technical-noun modifier. Never as a verb form ("the engine is running" → "the engine operates"). |
| Past participle | Use only as an adjective ("a damaged seal"), never to build a tense. |
| Verb forms | Use only: infinitive, imperative, simple present, simple past, simple future. No "has been", "would have", "is being", "should be done". |
| Noun clusters | Max 3 words. "engine oil pressure sensor output" → "the output of the engine oil pressure sensor"… still 4 → "the output from the oil pressure sensor". Use hyphens to show which words belong together. |
| Articles & small words | Do not delete "the", "a", "this", verbs or subjects to make text short. Use articles before nouns. |
| Phrasal verbs | Do not use them ("set up", "carry out", "find out", "look into"). Use the single approved verb ("install", "do", "find", "examine"). |
| Consistency | Same term for the same thing everywhere. Do not change "valve" to "regulator" for style. |

Common substitutions (illustrative, not the dictionary):

| Avoid | Use |
|---|---|
| utilize, employ | use |
| ensure, assure | make sure |
| perform, carry out | do |
| around, about (with numbers) | approximately |
| commence, initiate | start |
| terminate | stop |
| prior to | before |
| in order to | to |
| due to, because of the fact that | because (of) |
| obtain, acquire | get |
| require | need / must |
| indicate | show |
| locate | find / put (meaning dependent) |
| allow, enable | let / make it possible |
| however (sentence start) | but |
| numerous | many |
| verify | make sure / examine |
| may (permission) | can |
| should | must (for an instruction) |

When unsure whether a word is approved, choose the simplest common word with
one meaning, and keep that choice the same in the whole page.

## 2. Noun phrases
- Max 3 nouns in a cluster (see above).
- Make long phrases simpler with prepositions ("the pressure *of* the oil").

## 3. Verbs
- Approved tenses only (see Words).
- Use the **active voice**. In descriptive text, use passive only when the
  agent is unknown or not important and the active is not possible.
- Use the imperative for instructions ("Open the valve.").
- Do not change a verb into a noun ("do an inspection of" → "examine").

## 4. Sentences
- **One topic per sentence.**
- Procedural sentence: **max 20 words**.
- Descriptive sentence: **max 25 words**.
- Do not use semicolons to join sentences. Use colons only before lists.
- Use vertical lists for complex text.
- Use connecting words ("then", "but", "because", "if") to join sentences in
  a logical way.

## 5. Procedures (instructions)
- One instruction in each sentence. Two actions only when they occur at the
  same time ("Push and hold the button.").
- Write the instruction in the **imperative**.
- If there is a condition, put it **first**: "If the light comes on, stop the
  pump."
- Number the steps. One action per step.
- Write notes to give information, not instructions.

## 6. Descriptive writing
- Give the most important information first (top-down).
- One topic per paragraph. **Max 6 sentences per paragraph.**
- Use a heading for each topic.
- Use key words (keep the same name for the same thing) to link sentences.

## 7. Safety instructions (warnings and cautions)
- **WARNING** = risk of injury or death. **CAUTION** = risk of damage to
  equipment, data or the result.
- Start with a short, clear command ("Do not touch…", "Wear…").
- Then give the risk in a short sentence ("The surface is hot.").
- Put the warning or caution **before** the step it applies to.
- In a learning page, use NOTE for extra information that is not a step.

## 8. Punctuation and word count
- Count a number, symbol, or abbreviation as one word.
- A hyphenated group ("bottom-center", "high-pressure") counts as one word.
- Do not use semicolons. Use parentheses rarely.
- Headings, list items, table cells, and figure labels do not count toward
  the paragraph limit, but list items still follow the sentence limits.

---

## STE self-check before you publish

1. Run `python3 scripts/ste_lint.py page.html` and fix every **ERROR**.
2. Read each **WARN** and fix it unless it is a technical noun in the glossary.
3. Read the page top-down: does each section start with its main point?
4. Do all technical nouns appear in the glossary with the same spelling?
