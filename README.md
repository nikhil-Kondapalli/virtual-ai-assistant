# Virtual AI Assistant  

> **A scalable, real-time AI-powered avatar platform with Live2D, WebSockets, LLM integration, and TTS – built for immersive interactions and future AR/VR experiences.**  

---

## 🚀 Overview  

`virtual-ai-assistant` is not just another chatbot. It’s a **next-generation virtual companion** that combines **conversational AI** with **visual animation and real-time speech**, enabling truly **immersive and interactive experiences**.  

Unlike most AI apps that are text-only or voice-only, this project fuses:  
- **Live2D animated avatars** that react dynamically.  
- **Real-time WebSocket streaming** for low-latency conversations.  
- **LLM-driven intelligence** with token-level streaming output.  
- **Scalable TTS engine** that generates natural, real-time speech.  
- **Modular architecture** ready to extend into **AR/VR models** and **3D avatars**.  

This makes it ideal for **virtual assistants, education, entertainment, customer engagement, or immersive metaverse platforms.**  

---

## ✨ Key Features  

- 🎭 **Dynamic Avatars (Live2D)** – Expressive animations synced with speech and emotions.  
- ⚡ **Real-Time Streaming** – WebSocket-powered LLM + TTS for instant response without waiting.  
- 🗣️ **Voice Output (TTS)** – Natural speech generated chunk-by-chunk, streamable in the browser.  
- 🤝 **Two-Way Interaction** – User text input + assistant speech + avatar reactions.  
- 🏗️ **Scalable Microservices** – Each worker (LLM, TTS, Animation) runs in Docker for horizontal scaling.  
- 🌍 **Future-Ready** – Designed to evolve into AR/VR environments and fully AI-generated models.  

---

## 🛠️ Tech Stack  

- **Frontend:** React + Zustand + WebSocket Context API  
- **Avatar Rendering:** Live2D Viewer (extendable to WebGL/Three.js for 3D)  
- **Backend:** FastAPI + Django (Hybrid)  
- **AI/LLM:** Ollama or pluggable open/free LLMs  
- **TTS:** Glow-TTS (via Coqui TTS Docker)  
- **Messaging Layer:** Redis Pub/Sub  
- **Deployment:** Docker & Docker Compose  

---

## 🔥 Why This Project is Different  

Most AI assistants today are **either text-based chatbots** or **voice-only agents**. Even when avatars are added, they are usually **static or pre-scripted**.  

**Virtual AI Assistant is unique because:**  
- It merges **speech, text, and animated avatars** into a single pipeline.  
- It is **real-time** (token-level updates, not full-response waiting).  
- It uses a **microservice-first architecture**, making it easy to scale to millions of users.  
- It is **LLM-agnostic**: plug in any model (local Ollama, OpenAI, or custom fine-tuned).  
- It is designed with **AR/VR in mind**, meaning today’s Live2D avatars can evolve into **3D holograms or metaverse companions** tomorrow.  

---

## 📈 Roadmap  

- [x] Real-time LLM streaming (via WebSockets)  
- [x] Live2D avatar integration  
- [x] TTS with Glow-TTS (chunked streaming)  
- [ ] Multi-language support  
- [ ] Emotion-driven animation sync  
- [ ] AR/VR avatar rendering (Three.js / Unreal Engine bridges)  
- [ ] Cloud-native scaling (Kubernetes + microservices)  

---

## 📸 Demo Preview  

> 🎥 *Coming soon – animated demo of real-time avatar interaction with voice!*  

---

## 🤝 Contributing  

Contributions, issues, and feature requests are welcome!  
Feel free to check the [issues page](../../issues).  

---

## 📜 License  

This project is licensed under the **MIT License** – see the [LICENSE](./LICENSE) file for details.  
