import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

st.markdown(
    """
    <style>
        .stApp {
            background-color: #283149;
            color: #F5A623;
            text-align: center;
        }
        h1, h2, h3, h4, h5, h6, label, span, div {
            color: #F5A623 !important;
        }
        .bk-btn {
            background-color: #F5A623 !important;
            color: #283149 !important;
            border: 2px solid #283149 !important;
            font-size: 18px !important;
            padding: 12px 24px !important;
            border-radius: 10px !important;
        }
        .button-container {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
        }
        .stSelectbox, .stButton {
            background-color: #F5A623;
            border-radius: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 style="color: #F5A623; text-align: center;">Bienvenido al Traductor Mágico</h1>', unsafe_allow_html=True)
st.subheader("¡Dime qué quieres traducir y te lo diré en otro idioma!")

with st.sidebar:
    st.subheader("Configuración del Traductor")
    st.write("Pulsa el botón para empezar a hablar y elige los idiomas para traducir.")

st.write("Haz clic en el botón para empezar a hablar y traducir tu texto!")

stt_button = Button(label=" ¡Hablar! 🎤", width=350, height=60)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        st.write(f"Texto detectado: {result.get('GET_TEXT')}")
    try:
        os.mkdir("temp")
    except:
        pass
    st.title("Conversión de Texto a Audio")
    translator = Translator()
    
    text = str(result.get("GET_TEXT"))
    in_lang = st.selectbox(
        "Selecciona el idioma de entrada",
        ("Inglés", "Español", "Francés", "Alemán", "Italiano", "Japonés"),
    )
    if in_lang == "Inglés":
        input_language = "en"
    elif in_lang == "Español":
        input_language = "es"
    elif in_lang == "Francés":
        input_language = "fr"
    elif in_lang == "Alemán":
        input_language = "de"
    elif in_lang == "Italiano":
        input_language = "it"
    elif in_lang == "Japonés":
        input_language = "ja"
    
    out_lang = st.selectbox(
        "Selecciona el idioma de salida",
        ("Inglés", "Español", "Francés", "Alemán", "Italiano", "Japonés"),
    )
    if out_lang == "Inglés":
        output_language = "en"
    elif out_lang == "Español":
        output_language = "es"
    elif out_lang == "Francés":
        output_language = "fr"
    elif out_lang == "Alemán":
        output_language = "de"
    elif out_lang == "Italiano":
        output_language = "it"
    elif out_lang == "Japonés":
        output_language = "ja"
    
    def text_to_speech(input_language, output_language, text):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text
    
    display_output_text = st.checkbox("Mostrar el texto traducido")
    
    if st.button("Convertir a Audio"):
        result, output_text = text_to_speech(input_language, output_language, text)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("### Tu Audio Traducido:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
    
        if display_output_text:
            st.markdown("### Texto Traducido:")
            st.write(f"{output_text}")
    
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)

    remove_files(7)

image = Image.open('traductor.png') 

st.image(image, caption='¡Diviértete con tus traducciones!')
