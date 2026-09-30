import io
import base64
import httpx
import streamlit as st
from openai import OpenAI
from PIL import Image, ImageOps

# ---------------------------------------------------------
# ۱. تنظیمات اولیه صفحه
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dark Desert Studio",
    page_icon="🏜️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تابع کمکی برای خواندن امن Secret بدون کرش کردن روی سیستم محلی
def get_secret(key, default_value=""):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return default_value

# ---------------------------------------------------------
# ۲. سیستم امنیتی ورود با رمز عبور (Password Protection)
# ---------------------------------------------------------
def check_password():
    """بررسی رمز عبور جهت جلوگیری از دسترسی افراد غیرمجاز"""
    def password_entered():
        correct_pass = get_secret("APP_PASSWORD", "AmirAli@2026")
        if st.session_state.get("password_input") == correct_pass:
            st.session_state["password_correct"] = True
            if "password_input" in st.session_state:
                del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔒 ورود به استودیوی دارک دزرت</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>برای دسترسی به ابزارهای تولید محتوا، رمز عبور را وارد کنید.</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("رمز عبور دسترسی:", type="password", on_change=password_entered, key="password_input")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<h2 style='text-align: center;'>🔒 ورود به استودیوی دارک دزرت</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("رمز عبور دسترسی:", type="password", on_change=password_entered, key="password_input")
            st.error("⛔ رمز عبور اشتباه است! لطفاً مجدداً تلاش کنید.")
        return False
    return True

# تا زمانی که رمز عبور صحیح وارد نشده، اجرای برنامه متوقف می‌شود
if not check_password():
    st.stop()

# ---------------------------------------------------------
# ۳. خواندن ایمن تنظیمات و کلاینت هوش مصنوعی
# ---------------------------------------------------------
API_KEY = get_secret("OPENAI_API_KEY", "sk-gfcVewh9YAisYkmJ7DtkmNcTvBOFVL4795GLuRmqpNolXDMk")
BASE_URL = get_secret("OPENAI_BASE_URL", "https://api.gapgpt.ir/v1")

# ایجاد کلاینت امن برای ارتباط شبکه بدون خطای SSL
http_client = httpx.Client(verify=False, trust_env=False)
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    http_client=http_client
)

# دکمه خروج در سایدبار
with st.sidebar:
    st.markdown("### 👤 وضعیت دسترسی")
    st.success("ورود موفقیت‌آمیز")
    if st.button("🚪 خروج از حساب", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()
    st.markdown("---")

# ---------------------------------------------------------
# ۴. پردازش و تغییر اندازه حرفه‌ای تصاویر (Pillow)
# ---------------------------------------------------------
def process_and_resize_image(image_bytes, target_w, target_h, fit_mode="pad", bg_color=(15, 15, 20)):
    """تغییر اندازه و تطبیق تصویر با ابعاد درخواستی دقیق"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    if fit_mode == "stretch":
        resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    elif fit_mode == "crop":
        resized = ImageOps.fit(img, (target_w, target_h), method=Image.Resampling.LANCZOS)
    else:  # pad
        img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
        resized = Image.new("RGB", (target_w, target_h), bg_color)
        offset = ((target_w - img.width) // 2, (target_h - img.height) // 2)
        resized.paste(img, offset)
    
    out_buf = io.BytesIO()
    resized.save(out_buf, format="JPEG", quality=95)
    return out_buf.getvalue()

# ---------------------------------------------------------
# ۵. ساختار رابط کاربری و تب‌های برنامه
# ---------------------------------------------------------
st.title("🏜️ Dark Desert Creative Studio")
st.caption("سیستم هوشمند تولید سناریو، محتوای چندزبانه و استودیو پردازش تصویر")

tab_scenario, tab_translate, tab_image = st.tabs([
    "📜 تولید سناریو یوتیوب",
    "🌍 بازنویسی و ترجمه",
    "🎨 استودیو تولید تصویر"
])

# =========================================================
# تب اول: تولید سناریو یوتیوب
# =========================================================
with tab_scenario:
    st.subheader("تولید سناریوی کامل برای Dark Desert")
    
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("موضوع داستان / موجود افسانه‌ای:", value="دیو آل در باورهای ایرانی")
        tone = st.selectbox("لحن روایت:", ["ترسناک و رازآلود (Dark/Mysterious)", "مستندگونه و عمیق (Documentary)", "سینمایی و دراماتیک (Cinematic)"])
    with col2:
        duration = st.selectbox("طول ویدیو (تخمینی):", ["کوتاه (Shorts / Reels - زیر ۶۰ ثانیه)", "متوسط (۵ تا ۸ دقیقه)", "کامل و بلند (۱۰ تا ۱۵ دقیقه)"])
        lang_target = st.selectbox("زبان خروجی سناریو:", ["انگلیسی (مخاطب جهانی یوتیوب)", "فارسی", "دوزبانه (فارسی به همراه نسخه انگلیسی)"])

    extra_notes = st.text_area("نکات کلیدی یا جزییات خاص داستان:", placeholder="مثلاً: شروع با یک حادثه شبانه در کویر، تاکید بر عناصر فولکلور...")

    if st.button("✨ تولید سناریو و پرامپت‌های صحنه", type="primary"):
        with st.spinner("هوش مصنوعی در حال نگارش سناریو و تدوین پرامپت‌ها..."):
            try:
                system_prompt = (
                    "You are a master scriptwriter and visual director for the YouTube channel 'Tales from the Dark Desert'. "
                    "You specialize in Middle Eastern and Persian folklore, eerie myths, and dark desert horror. "
                    "Format the output clearly: [Title], [Hook], [Scene-by-Scene Script with Midjourney/Veo visual prompts], [Voiceover narration]."
                )
                user_msg = f"Topic: {topic}\nTone: {tone}\nTarget Duration: {duration}\nLanguage: {lang_target}\nExtra Details: {extra_notes}"
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg}
                    ],
                    temperature=0.7
                )
                output_text = response.choices[0].message.content
                st.markdown("### 🎬 سناریوی آماده:")
                st.markdown(output_text)
                st.download_button("📥 دانلود متن سناریو (.txt)", data=output_text, file_name="script.txt", mime="text/plain")
            except Exception as e:
                st.error(f"خطا در تولید سناریو: {str(e)}")

# =========================================================
# تب دوم: بازنویسی و ترجمه تخصصی
# =========================================================
with tab_translate:
    st.subheader("موتور تبدیل، بازنویسی و ادیت محتوا")
    
    input_text = st.text_area("متن ورودی (فارسی یا انگلیسی):", height=180, placeholder="متن خود را اینجا وارد کنید...")
    mode = st.radio("عملیات مورد نظر:", [
        "ترجمه به انگلیسی غنی و داستانی (مناسب نریشن Dark Desert)",
        "بازنویسی لحن املاک تورنتو (هدایتی رئال استیت - اینستاگرام)",
        "خلاصه‌سازی در قالب پست اسلایدی",
        "اصلاح گرامر و افزایش جذابیت (Polishing)"
    ], horizontal=True)

    if st.button("🚀 پردازش متن"):
        if not input_text.strip():
            st.warning("لطفاً ابتدا متنی وارد کنید.")
        else:
            with st.spinner("در حال پردازش متن..."):
                try:
                    sys_instruction = "You are an expert bilingual content editor and copywriter."
                    if "Dark Desert" in mode:
                        sys_instruction += " Translate and rewrite this into immersive, chilling, high-vocabulary English suitable for dark folklore YouTube narration."
                    elif "هدایتی" in mode:
                        sys_instruction += " Rewrite this for a luxury Toronto real estate Instagram page (Alireza Hedayati, RE/MAX Realtron). Tone: Professional, trustworthy, engaging for Iranian-Canadians."
                    elif "اسلایدی" in mode:
                        sys_instruction += " Break this content into 5-7 punchy, engaging carousel slides with hook and CTA."
                    
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": sys_instruction},
                            {"role": "user", "content": input_text}
                        ]
                    )
                    st.markdown("### 📝 نتیجه نهایی:")
                    st.markdown(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"خطا در پردازش: {str(e)}")

# =========================================================
# تب سوم: استودیو تولید تصویر
# =========================================================
with tab_image:
    st.subheader("تولید و ترکیب‌بندی هوشمند تصویر (DALL-E 3 & Custom Canvas)")
    
    profile = st.selectbox("پروفایل سبک:", [
        "Dark Desert Cinematic (فولکلور و تاریک)",
        "Hedayati Real Estate (معماری مدرن و تمیز)",
        "Social Media Clean (پست‌های گرافیکی)",
        "Smart Universal (توصیف آزاد)"
    ])

    aspect_option = st.selectbox("نسبت ابعاد خروجی نهایی:", [
        "YouTube Thumbnail / Landscape (1920x1080 - 16:9)",
        "Instagram / TikTok Reel (1080x1920 - 9:16)",
        "Instagram Square Post (1080x1080 - 1:1)",
        "Instagram Portrait Post (1080x1350 - 4:5)",
        "ابعاد دلخواه (Custom Size)"
    ])

    if aspect_option == "ابعاد دلخواه (Custom Size)":
        c_w, c_h = st.columns(2)
        with c_w:
            target_width = st.number_input("عرض (Width به پیکسل):", min_value=256, max_value=3840, value=1280, step=10)
        with c_h:
            target_height = st.number_input("ارتفاع (Height به پیکسل):", min_value=256, max_value=3840, value=720, step=10)
    else:
        if "1920x1080" in aspect_option:
            target_width, target_height = 1920, 1080
        elif "1080x1920" in aspect_option:
            target_width, target_height = 1080, 1920
        elif "1080x1080" in aspect_option:
            target_width, target_height = 1080, 1080
        elif "1080x1350" in aspect_option:
            target_width, target_height = 1080, 1350

    creation_mode = st.radio("روش توصیف تصویر:", ["توصیف آزاد (یکپارچه)", "ترکیب‌بندی پنج‌عنصری (دقیق و هوشمند)"], horizontal=True)

    if creation_mode == "توصیف آزاد (یکپارچه)":
        raw_prompt = st.text_area("پرامپت یا ایده تصویر:", placeholder="مثلاً: A terrifying demon standing in the windswept sand dunes under moonlight...")
    else:
        e1, e2 = st.columns(2)
        with e1:
            subject = st.text_input("۱. سوژه اصلی (Subject):", placeholder="مثال: موجود شیطانی آل")
            environment = st.text_input("۲. محیط و پس‌زمینه (Setting):", placeholder="مثال: روستای متروکه کویری در ایران")
            lighting = st.text_input("۳. نورپردازی (Lighting):", placeholder="مثال: مهتاب کم‌رمق، سایه‌های بلند تاریک")
        with e2:
            details = st.text_input("۴. جزییات و بافت (Details):", placeholder="مثال: ردپا روی شن، پارچه پاره کهنه")
            style = st.text_input("۵. سبک و رنگ (Mood/Style):", placeholder="مثال: Cinematic, dark volumetric mist, hyper-detailed")
        raw_prompt = f"Subject: {subject}. Environment: {environment}. Lighting: {lighting}. Details: {details}. Mood and Style: {style}."

    if st.button("🎨 تولید تصویر با هوش مصنوعی", type="primary"):
        if not raw_prompt.strip():
            st.warning("لطفاً توصیف تصویر را وارد کنید.")
        else:
            with st.spinner("در حال ساخت پرامپت حرفه‌ای و پردازش با DALL-E 3..."):
                try:
                    enhancer_sys = (
                        "You are an expert image prompt engineer. Convert the user's idea into an ultra-detailed, photorealistic "
                        "English prompt for DALL-E 3. Avoid text in the image. Profile: " + profile
                    )
                    prompt_res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": enhancer_sys},
                            {"role": "user", "content": raw_prompt}
                        ]
                    )
                    final_prompt = prompt_res.choices[0].message.content

                    base_dalle_size = "1024x1024"
                    if target_width > target_height:
                        base_dalle_size = "1792x1024"
                    elif target_height > target_width:
                        base_dalle_size = "1024x1792"

                    img_response = client.images.generate(
                        model="dall-e-3",
                        prompt=final_prompt,
                        size=base_dalle_size,
                        quality="standard",
                        response_format="b64_json",
                        n=1
                    )
                    raw_b64 = img_response.data[0].b64_json
                    raw_bytes = base64.b64decode(raw_b64)

                    final_image_bytes = process_and_resize_image(raw_bytes, target_width, target_height, fit_mode="pad")

                    st.success("✅ تصویر با موفقیت تولید و به ابعاد درخواستی تبدیل شد!")
                    st.image(final_image_bytes, caption=f"خروجی نهایی ({target_width}x{target_height})", use_container_width=True)
                    
                    with st.expander("🔍 مشاهده پرامپت نهایی تولیدشده"):
                        st.write(final_prompt)

                    st.download_button(
                        label="📥 دانلود تصویر با کیفیت کامل",
                        data=final_image_bytes,
                        file_name=f"studio_image_{target_width}x{target_height}.jpg",
                        mime="image/jpeg"
                    )
                except Exception as err:
                    st.error(f"خطا در تولید تصویر: {str(err)}")
