import gradio as gr
import random
import html
from bpe import tok, bpe_encode_string


# -------------------------
# Token coloring (nice UI)
# -------------------------
def random_soft_color():
    h = random.randint(0, 360)
    s = random.randint(30, 70)
    l = random.randint(75, 90)
    return f"hsl({h}, {s}%, {l}%)"


def color_token(token):
    escaped = html.escape(token)
    color = random_soft_color()
    return f"""
    <span style="
        background:{color};
        padding:4px 6px;
        margin:3px;
        border-radius:6px;
        font-size:16px;
        display:inline-block;
    ">{escaped}</span>
    """


# -------------------------
# Main callback
# -------------------------
def tokenize_ui(text):
    if not text.strip():
        return "", "", "", 0

    ids, toks = bpe_encode_string(text)

    # NEW LOGIC: handle newline properly
    parts = []
    for t in toks:
        if t == "\n":
            parts.append("<br>")  # break line visually
        else:
            parts.append(color_token(t))

    colored_html = "".join(parts)

    return colored_html, ids, toks, len(ids)



# -------------------------
# Custom CSS
# -------------------------
custom_css = """
.container {
    max-width: 1300px !important;
}
#tokenbox {
    height: 260px;
    overflow-y: auto;
    border-radius: 10px;
}
#inputbox textarea {
    font-size: 19px !important;
    height: 280px !important;
}
.token-output {
    padding: 12px;
    background: #f8f8f8;
    border-radius: 8px;
}
"""


# -------------------------
# Build UI
# -------------------------

with gr.Blocks(css=custom_css, title="Hindi BPE Tokenizer") as demo:

    gr.Markdown(
        """
        <h1 style="text-align:center; font-size:42px; margin-bottom:10px;">
            🇮🇳 Hindi BPE Tokenizer
        </h1>
        <p style="text-align:center; font-size:18px; color:#444;">
            A custom subword tokenizer trained from scratch on Hindi text.
        </p>
        """
    )

    with gr.Row():
        with gr.Column(scale=5):
            input_box = gr.Textbox(
                label="Input Text",
                placeholder="Type Hindi text here…",
                lines=12,
                elem_id="inputbox"
            )
        with gr.Column(scale=5):
            token_count = gr.Number(label="Token Count", value=0, interactive=False)
            colored_tokens = gr.HTML(label="Tokens", elem_id="tokenbox")

    with gr.Row():
        ids_json = gr.JSON(label="Token IDs")
        toks_json = gr.JSON(label="Token Strings")

    input_box.change(
        tokenize_ui,
        inputs=[input_box],
        outputs=[colored_tokens, ids_json, toks_json, token_count]
    )

demo.launch(debug=True)
