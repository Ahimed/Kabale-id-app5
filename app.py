import streamlit as st
import pandas as pd
from datetime import datetime
import os
import qrcode
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DB_FILE = "kabalee_id_database.csv"
PHOTO_DIR = "captured_photos"
PDF_DIR = "generated_ids"

if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=[
            "ID_Lakkoofsa", "Maqaa Guutuu", "Saala", "Umrii", 
            "Ganda/Garee", "Lakk_Bilbilaa", "Guyyaa_Galmee", "Suuraa_Path"
        ])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def create_id_pdf(row, qr_path):
    pdf_filename = os.path.join(PDF_DIR, f"ID_{row['ID_Lakkoofsa']}.pdf")
    doc = SimpleDocTemplate(pdf_filename, pagesize=(400, 250),
                            rightMargin=15, leftMargin=15, topMargin=15, bottomMargin=15)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=12,
        textColor=colors.HexColor('#1b4332'),
        alignment=1,
        spaceAfter=10
    )
    
    text_style = ParagraphStyle(
        'TextStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=4
    )

    story.append(Paragraph("<b>BULCHIINSA GANDA QOOLOO SIRRII</b><br/><font size=8>Waraqaa Ragaa Ibsituu Jiraataa (ID Card)</font>", title_style))
    story.append(Spacer(1, 5))
    
    photo_p = row['Suuraa_Path'] if (pd.notna(row['Suuraa_Path']) and os.path.exists(row['Suuraa_Path'])) else ""
    
    if photo_p and os.path.exists(photo_p):
        img_obj = Image(photo_p, width=70, height=85)
    else:
        img_obj = Paragraph("Suuraa Hin Jiru", text_style)
        
    qr_obj = Image(qr_path, width=75, height=75) if os.path.exists(qr_path) else Paragraph("QR Hin Jiru", text_style)
    
    info_html = f"""
    <b>Lakkoofsa ID:</b> {row['ID_Lakkoofsa']}<br/>
    <b>Maqaa:</b> {row['Maqaa Guutuu']}<br/>
    <b>Saala / Umrii:</b> {row['Saala']}, {row['Umrii']}<br/>
    <b>Garee/Ganda:</b> {row['Ganda/Garee']}<br/>
    <b>Bilbila:</b> {row['Lakk_Bilbilaa']}<br/>
    <b>Guyyaa Kenname:</b> {row['Guyyaa_Galmee']}
    """
    info_p = Paragraph(info_html, text_style)
    
    data_table = Table([[img_obj, info_p, qr_obj]], colWidths=[80, 200, 90])
    data_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    
    story.append(data_table)
    doc.build(story)
    return pdf_filename

st.set_page_config(page_title="Sirna Galmee ID Kabalee", page_icon="🪪", layout="centered")

st.title("🪪 Galmee ID Jiraataa fi Kaameraa (Camera Capture)")
st.markdown("Odeeffannoo jiraataa galmeessuun kallattiidhaan kaameradhaan suuraa kaasaa.")

menu = st.sidebar.selectbox("Filannoo", ["Jiraataa Galmeessi", "Galmee Ilaali"])

df = load_data()

if menu == "Jiraataa Galmeessi":
    st.subheader("📝 Galmee Odeeffannoo Haaraa fi Kaameraa")
    
    with st.form("id_form"):
        col1, col2 = st.columns(2)
        with col1:
            maqaa = st.text_input("Maqaa Guutuu (Akkuma waraqaa ragaatti)")
            saala = st.selectbox("Saala", ["Dhiira", "Dubartii"])
            umrii = st.number_input("Umrii", min_value=1, max_value=120, value=20)
        with col2:
            ganda = st.text_input("Garee / Ganda Xiqqaa")
            bilbila = st.text_input("Lakkoofsa Bilbilaa")
            
        st.markdown("---")
        st.write("📸 **Suuraa Kaasuu (Camera Input):**")
        # Bakki itti kaameran suuraa fuudhu
        camera_photo = st.camera_input("Kaameraa banuuf 'Take Photo' tuqi")
        
        submit_button = st.form_submit_button(label="ID Galmeessi fi Qopheessi")
        
        if submit_button:
            if maqaa and ganda and bilbila:
                random_id = f"KAB-{datetime.now().strftime('%Y')}-{len(df) + 1:03d}"
                guyyaa = datetime.now().strftime("%Y-%m-%d")
                
                # Suuraa kaameran kaafame kuusuu
                photo_path = ""
                if camera_photo is not None:
                    photo_path = os.path.join(PHOTO_DIR, f"{random_id}.jpg")
                    with open(photo_path, "wb") as f:
                        f.write(camera_photo.getbuffer())
                
                new_row = {
                    "ID_Lakkoofsa": random_id,
                    "Maqaa Guutuu": maqaa,
                    "Saala": saala,
                    "Umrii": umrii,
                    "Ganda/Garee": ganda,
                    "Lakk_Bilbilaa": bilbila,
                    "Guyyaa_Galmee": guyyaa,
                    "Suuraa_Path": photo_path
                }
                
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                
                # QR Code uumuu
                qr_data = f"ID: {random_id}\nMaqaa: {maqaa}\nGanda: {ganda}\nBilbila: {bilbila}"
                qr_img = generate_qr(qr_data)
                qr_path = os.path.join(PHOTO_DIR, f"qr_{random_id}.png")
                qr_img.save(qr_path)
                
                # PDF uumuu
                pdf_path = create_id_pdf(new_row, qr_path)
                
                st.success(f"Milkaa'inaan galmeeffameera! Lakkoofsi ID: **{random_id}**")
                
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📥 Waraqaa Ragaa ID (PDF) Buusi",
                        data=pdf_file,
                        file_name=f"ID_{random_id}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.warning("Maaloo odeeffannoo barbaachisaa hunda guuti!")

elif menu == "Galmee Ilaali":
    st.subheader("📋 Galmee Jiraattotaa")
    if not df.empty:
        search_query = st.text_input("Maqaa ykn Lakkoofsa ID tiin barbaadi:")
        if search_query:
            filtered_df = df[df['Maqaa Guutuu'].str.contains(search_query, case=False, na=False) | 
                             df['ID_Lakkoofsa'].str.contains(search_query, case=False, na=False)]
        else:
            filtered_df = df
            
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("Galmeen tokkooyyuu hin jiru.")
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import qrcode
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DB_FILE = "kabalee_id_database.csv"
PHOTO_DIR = "captured_photos"
PDF_DIR = "generated_ids"

if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=[
            "ID_Lakkoofsa", "Maqaa Guutuu", "Saala", "Umrii", 
            "Ganda/Garee", "Lakk_Bilbilaa", "Guyyaa_Galmee", "Suuraa_Path"
        ])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def create_id_pdf(row, qr_path):
    pdf_filename = os.path.join(PDF_DIR, f"ID_{row['ID_Lakkoofsa']}.pdf")
    doc = SimpleDocTemplate(pdf_filename, pagesize=(400, 250),
                            rightMargin=15, leftMargin=15, topMargin=15, bottomMargin=15)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=12,
        textColor=colors.HexColor('#1b4332'),
        alignment=1,
        spaceAfter=10
    )
    
    text_style = ParagraphStyle(
        'TextStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=4
    )

    story.append(Paragraph("<b>BULCHIINSA GANDA QOOLOO SIRRII</b><br/><font size=8>Waraqaa Ragaa Ibsituu Jiraataa (ID Card)</font>", title_style))
    story.append(Spacer(1, 5))
    
    photo_p = row['Suuraa_Path'] if (pd.notna(row['Suuraa_Path']) and os.path.exists(row['Suuraa_Path'])) else ""
    
    if photo_p and os.path.exists(photo_p):
        img_obj = Image(photo_p, width=70, height=85)
    else:
        img_obj = Paragraph("Suuraa Hin Jiru", text_style)
        
    qr_obj = Image(qr_path, width=75, height=75) if os.path.exists(qr_path) else Paragraph("QR Hin Jiru", text_style)
    
    info_html = f"""
    <b>Lakkoofsa ID:</b> {row['ID_Lakkoofsa']}<br/>
    <b>Maqaa:</b> {row['Maqaa Guutuu']}<br/>
    <b>Saala / Umrii:</b> {row['Saala']}, {row['Umrii']}<br/>
    <b>Garee/Ganda:</b> {row['Ganda/Garee']}<br/>
    <b>Bilbila:</b> {row['Lakk_Bilbilaa']}<br/>
    <b>Guyyaa Kenname:</b> {row['Guyyaa_Galmee']}
    """
    info_p = Paragraph(info_html, text_style)
    
    data_table = Table([[img_obj, info_p, qr_obj]], colWidths=[80, 200, 90])
    data_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1b4332')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    
    story.append(data_table)
    doc.build(story)
    return pdf_filename

st.set_page_config(page_title="Sirna Galmee ID Kabalee", page_icon="🪪", layout="centered")

st.title("🪪 Galmee ID Jiraataa fi Kaameraa (Camera Capture)")
st.markdown("Odeeffannoo jiraataa galmeessuun kallattiidhaan kaameradhaan suuraa kaasaa.")

menu = st.sidebar.selectbox("Filannoo", ["Jiraataa Galmeessi", "Galmee Ilaali"])

df = load_data()

if menu == "Jiraataa Galmeessi":
    st.subheader("📝 Galmee Odeeffannoo Haaraa fi Kaameraa")
    
    with st.form("id_form"):
        col1, col2 = st.columns(2)
        with col1:
            maqaa = st.text_input("Maqaa Guutuu (Akkuma waraqaa ragaatti)")
            saala = st.selectbox("Saala", ["Dhiira", "Dubartii"])
            umrii = st.number_input("Umrii", min_value=1, max_value=120, value=20)
        with col2:
            ganda = st.text_input("Garee / Ganda Xiqqaa")
            bilbila = st.text_input("Lakkoofsa Bilbilaa")
            
        st.markdown("---")
        st.write("📸 **Suuraa Kaasuu (Camera Input):**")
        # Bakki itti kaameran suuraa fuudhu
        camera_photo = st.camera_input("Kaameraa banuuf 'Take Photo' tuqi")
        
        submit_button = st.form_submit_button(label="ID Galmeessi fi Qopheessi")
        
        if submit_button:
            if maqaa and ganda and bilbila:
                random_id = f"KAB-{datetime.now().strftime('%Y')}-{len(df) + 1:03d}"
                guyyaa = datetime.now().strftime("%Y-%m-%d")
                
                # Suuraa kaameran kaafame kuusuu
                photo_path = ""
                if camera_photo is not None:
                    photo_path = os.path.join(PHOTO_DIR, f"{random_id}.jpg")
                    with open(photo_path, "wb") as f:
                        f.write(camera_photo.getbuffer())
                
                new_row = {
                    "ID_Lakkoofsa": random_id,
                    "Maqaa Guutuu": maqaa,
                    "Saala": saala,
                    "Umrii": umrii,
                    "Ganda/Garee": ganda,
                    "Lakk_Bilbilaa": bilbila,
                    "Guyyaa_Galmee": guyyaa,
                    "Suuraa_Path": photo_path
                }
                
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                
                # QR Code uumuu
                qr_data = f"ID: {random_id}\nMaqaa: {maqaa}\nGanda: {ganda}\nBilbila: {bilbila}"
                qr_img = generate_qr(qr_data)
                qr_path = os.path.join(PHOTO_DIR, f"qr_{random_id}.png")
                qr_img.save(qr_path)
                
                # PDF uumuu
                pdf_path = create_id_pdf(new_row, qr_path)
                
                st.success(f"Milkaa'inaan galmeeffameera! Lakkoofsi ID: **{random_id}**")
                
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📥 Waraqaa Ragaa ID (PDF) Buusi",
                        data=pdf_file,
                        file_name=f"ID_{random_id}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.warning("Maaloo odeeffannoo barbaachisaa hunda guuti!")

elif menu == "Galmee Ilaali":
    st.subheader("📋 Galmee Jiraattotaa")
    if not df.empty:
        search_query = st.text_input("Maqaa ykn Lakkoofsa ID tiin barbaadi:")
        if search_query:
            filtered_df = df[df['Maqaa Guutuu'].str.contains(search_query, case=False, na=False) | 
                             df['ID_Lakkoofsa'].str.contains(search_query, case=False, na=False)]
        else:
            filtered_df = df
            
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("Galmeen tokkooyyuu hin jiru.")
