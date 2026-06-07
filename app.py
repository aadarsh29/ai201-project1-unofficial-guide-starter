"""
app.py
Milestone 5: Gradio Web Interface
UMass Unofficial Guide RAG System

Run with: python app.py
Then open: http://localhost:7860
"""

import gradio as gr
from query import ask, initialize

# Initialize the pipeline once at startup
initialize()


def handle_query(question):
    """
    Handle a user query from the Gradio interface.
    Returns the answer and formatted source list as separate strings.
    """
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


# ─── GRADIO UI ─────────────────────────────────────────────────────────────

with gr.Blocks(title="UMass Unofficial Guide") as demo:

    gr.Markdown("""
    # 📚 UMass Unofficial Guide
    ### The student knowledge your advisor won't tell you
    Ask questions about professors and courses based on real student reviews.
    All answers are grounded in Rate My Professor reviews from UMass Amherst students.
    
    **Courses covered:** CICS 110, CICS 160, MATH 131, PHY 151, BIO 151
    """)

    with gr.Row():
        with gr.Column(scale=2):
            question_input = gr.Textbox(
                label="Your question",
                placeholder="e.g. Is David Hamilton good for PHY 151? What is the workload like for CICS 160?",
                lines=2
            )
            ask_button = gr.Button("Ask", variant="primary")

    with gr.Row():
        with gr.Column(scale=2):
            answer_output = gr.Textbox(
                label="Answer",
                lines=8,
                interactive=False
            )
        with gr.Column(scale=1):
            sources_output = gr.Textbox(
                label="Retrieved from",
                lines=8,
                interactive=False
            )

    gr.Markdown("""
    ---
    **Example questions to try:**
    - Is David Hamilton a good professor for PHY 151?
    - Which BIO 151 professor should I avoid?
    - What is the workload like for CICS 160 with Professor Davila?
    - Is Eric Heinzman good for MATH 131?
    - Which CICS 110 professor should I avoid?
    """)

    # Wire up the button and enter key
    ask_button.click(
        fn=handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output]
    )
    question_input.submit(
        fn=handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output]
    )

if __name__ == "__main__":
    demo.launch()