import gradio as gr
from dotenv import load_dotenv
from answer import answer_question

load_dotenv(override=True)


def format_context(context):
    result = "<h2 style='color: #ff7800;'>Relevant Context</h2>\n\n"
    for doc in context:
        result += f"<span style='color: #ff7800;'>Source: {doc.metadata['source']}</span>\n\n"
        result += doc.page_content + "\n\n"
    return result


def chat(history):
    # Extract the actual text content from the last message
    last_message_data = history[-1]
    
    if isinstance(last_message_data, dict):
        last_message_content = last_message_data.get("content", last_message_data.get(1, ""))
    elif isinstance(last_message_data, (list, tuple)) and len(last_message_data) >= 2:
        last_message_content = last_message_data[1] 
    else:
        last_message_content = str(last_message_data)
    
    if isinstance(last_message_content, list):
        last_message = " ".join(
            part.get("text", "") for part in last_message_content if isinstance(part, dict) and part.get("type") == "text"
        )
    else:
        last_message = str(last_message_content)
    
    # Build prior history, handling different formats
    prior = []
    for msg in history[:-1]:
        if isinstance(msg, dict):
            prior.append(msg)
        elif isinstance(msg, (list, tuple)) and len(msg) >= 2:
            prior.append({"role": "user", "content": msg[0]})
            if msg[1]:
                prior.append({"role": "assistant", "content": msg[1]})
    
    answer, context = answer_question(last_message, prior)
    history.append({"role": "assistant", "content": answer})
    return history, format_context(context)


def main():
    def put_message_in_chatbot(message, history):
        if history is None:
            history = []
        return "", history + [{"role": "user", "content": message}]

    theme = gr.themes.Soft(font=["Inter", "system-ui", "sans-serif"])

    with gr.Blocks(title="Insurellm Expert Assistant") as ui:
        gr.Markdown("# 🏢 Insurellm Expert Assistant\nAsk me anything about Insurellm!")

        with gr.Row():
            with gr.Column(scale=1):
                chatbot = gr.Chatbot(
                    label="💬 Conversation", 
                    height=600
                )
                message = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask anything about Insurellm...",
                    show_label=False,
                )

            with gr.Column(scale=1):
                context_markdown = gr.Markdown(
                    label="📚 Retrieved Context",
                    value="*Retrieved context will appear here*"
                )

        message.submit(
            put_message_in_chatbot, inputs=[message, chatbot], outputs=[message, chatbot]
        ).then(chat, inputs=chatbot, outputs=[chatbot, context_markdown])

    ui.launch(inbrowser=True, theme=theme)


if __name__ == "__main__":
    main()