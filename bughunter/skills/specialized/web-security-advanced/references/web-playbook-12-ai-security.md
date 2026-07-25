# AISecurity
English: AI Security
- Entry Count: 4
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## LLMPrompt injection attack
- ID: ai-prompt-injection
- Difficulty: beginner
- Subcategory: Prompt injection
- Tags: AI, LLM, Prompt Injection, ChatGPT, Prompt injection
- Original Extracted Source: original extracted web-security-wiki source/ai-prompt-injection.md
Description:
Overwrite or bypass through carefully constructed user inputLLM(Large language model)System prompt(System Prompt), makingAIExecute unintended operations. Including direct injection(DPI)And indirect injection(IPI), which can lead to system prompt leakage、Security barrier bypass、Data leakage and unauthorized operations.
Prerequisites:
- Target application integrated withLLM
- Can be withLLMInteractive input text
Execution Outline:
1. 1. System prompt leakage.
2. 2. Security barrier bypass
3. 3. Indirect hint injection(IPI)
4. 4. UtilizeAITool Invocation(Function Calling)
## AIModel theft and inference attacks
- ID: ai-model-extraction
- Difficulty: advanced
- Subcategory: Model attack
- Tags: AI, Model theft, Model Extraction, Member inference, APIAbuse
- Original Extracted Source: original extracted web-security-wiki source/ai-model-extraction.md
Description:
Through a large number of carefully crafted queriesAIConduct black-box attacks on the model to steal model parameters(Model Extraction)、Inference training data(Membership Inference)Or discover model decision boundaries. Attackers can build functionally equivalent substitute models or extract private data from this.
Prerequisites:
- Target provisionAIInferenceAPI
- APIReturn Probability/Confidence Score
Execution Outline:
1. 1. APIDetection and capability analysis
2. 2. Model theft(Model Extraction)
3. 3. Member inference attack(MIA)
4. 4. Training data extraction
## Adversarial sample attacks
- ID: ai-adversarial
- Difficulty: expert
- Subcategory: Adversarial attacks
- Tags: AI, Adversarial samples, Adversarial, FGSM, Evasion
- Original Extracted Source: original extracted web-security-wiki source/ai-adversarial.md
Description:
By adding imperceptible minute disturbances to the input data,AIThe model produces incorrect prediction results. Adversarial sample attacks can be applied to image classification、Text analysis、Voice recognition and variousAIModel, threat to autonomous driving、Security detection and content review system.
Prerequisites:
- Target usageAIMaking automated decisions
- Controllable input data
Execution Outline:
1. 1. White-box attack——FGSM
2. 2. Black box attack——Based on query
3. 3. Text adversarial attacks
4. 4. Physical world against attacks
## RAGPoisoning and Knowledge Base Injection
- ID: ai-rag-poisoning
- Difficulty: intermediate
- Subcategory: RAGAttack
- Tags: AI, RAG, Knowledge Base, Vector database, Data poisoning
- Original Extracted Source: original extracted web-security-wiki source/ai-rag-poisoning.md
Description:
UsageRAG(Retrieval-Augmented Generation)Architecture'sAIApplication, influence through poisoning documents in the knowledge baseAIAnswers. Attackers can inject documents containing malicious instructions into the vector database, and when users query to trigger retrieval, the malicious document is injected intoAIExecute indirect hint injection in context.
Prerequisites:
- Target usageRAGArchitecture
- Documents can be submitted to the knowledge base
- UnderstandRAGRetrieval mechanism
Execution Outline:
1. 1. RAGArchitecture identification and analysis.
2. 2. Knowledge base poisoning——Injecting malicious documents
3. 3. Trigger poisoning document retrieval
4. 4. Direct Attack on the Vector Database

