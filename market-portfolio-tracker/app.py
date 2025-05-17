import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
from user_utils import register_user, login_user, get_user_data, update_user_data

# Kur verilerini yükleme
@st.cache_data
def load_kur_data():
    df = pd.read_csv("kur_verileri.csv")
    df["tarih"] = pd.to_datetime(df["tarih"])
    return df

kur_df = load_kur_data()


def is_secure_password(password):
    if len(password) < 6:
        return False
    if re.search(r'012|123|234|345|456|567|678|789|890|987|876|765|654|543|432|321', password):
        return False
    if re.search(r'(\d)\1\1', password):
        return False
    return True


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""


if not st.session_state.logged_in:
    st.title("🔐 Giriş / Kayıt")
    menu = st.radio("Seçiminiz", ["Giriş Yap", "Kayıt Ol"])

    email = st.text_input("E-posta veya Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")

    if menu == "Kayıt Ol":
        if st.button("Kaydol"):
            msg = register_user(email, password)
            if "başarıyla" in msg:
                st.success(msg)
            else:
                st.error(msg)

    elif menu == "Giriş Yap":
        if st.button("Giriş Yap"):
            msg = login_user(email, password)
            if "Hoş geldin" in msg:
                st.success(msg)
                st.session_state.logged_in = True
                st.session_state.user_email = email
            else:
                st.error(msg)


else:
    st.success(f"👋 Hoş geldin, {st.session_state.user_email}")
    
    # Kullanıcı verilerini al
    user_data = get_user_data(st.session_state.user_email)
    if user_data:
        st.subheader("👛 Hesap Özeti")

        st.write(f"**Mevcut TL Bakiye:** {user_data['budget']:.2f} TL")

        st.write("**Portföy:**")
        for asset, amount in user_data["portfolio"].items():
            st.write(f"- {asset}: {amount}")

        
        st.subheader("💸 Al / Sat İşlemleri")

        
        prices = {
            "USD": kur_df["USD"].iloc[-1],      
            "EUR": kur_df["EUR"].iloc[-1], 
            "ALTIN": kur_df["GOLD"].iloc[-1],
            "BTC": kur_df["BTC"].iloc[-1]  
        }

        islem_tipi = st.radio("İşlem Tipi", ["Satın Al", "Sat"])

        birim = st.selectbox("Varlık Seç", ["USD", "EUR", "ALTIN", "BTC"])
        miktar = st.number_input("Miktar", min_value=0.0)

        if st.button("İşlemi Gerçekleştir"):
            if islem_tipi == "Satın Al":
                toplam_tutar = prices[birim] * miktar
                if user_data["budget"] >= toplam_tutar:
                    user_data["budget"] -= toplam_tutar
                    user_data["portfolio"][birim] += miktar
                    update_user_data(st.session_state.user_email, user_data)
                    st.success(f"{miktar} {birim} satın alındı!")
                else:
                    st.warning("Yetersiz TL bakiyesi.")
            else:  # Sat
                if user_data["portfolio"][birim] >= miktar:
                    toplam_tutar = prices[birim] * miktar
                    user_data["portfolio"][birim] -= miktar
                    user_data["budget"] += toplam_tutar
                    update_user_data(st.session_state.user_email, user_data)
                    st.success(f"{miktar} {birim} satıldı!")
                else:
                    st.warning("Yetersiz varlık miktarı.")

    else:
        st.warning("Kullanıcı verileri yüklenemedi.")

    
    st.header("💹 Piyasa Takip Ekranı")
    st.subheader("Altın, Döviz ve Bitcoin Verileri")

    selected_date = st.date_input("Tarih Seçiniz", value=datetime.today() - timedelta(days=1))
    formatted_date = selected_date.strftime("%d.%m.%Y")
    st.write(f"Seçilen Tarih: {formatted_date}")
    selected_row = kur_df[kur_df["tarih"].dt.date == selected_date]

    if not selected_row.empty:
        row = selected_row.iloc[0]
        row["TL"] = 1.0  


        st.header("📊 Seçilen Tarihteki Piyasa Değerleri")
        st.metric("Dolar (USD)", f"{row['USD']} TL")
        st.metric("Euro (EUR)", f"{row['EUR']} TL")
        st.metric("Bitcoin (BTC)", f"{row['BTC']:.2f} TL")
        st.metric("Altın (Gram)", f"{row['GOLD']} TL")

        st.header("💱 Döviz Çevirici")
        amount = st.number_input("Tutar", min_value=0.0)
        from_currency = st.selectbox("Kaynak Döviz", ["TL","USD", "EUR", "BTC", "GOLD"])
        to_currency = st.selectbox("Hedef Döviz", ["TL","USD", "EUR", "BTC", "GOLD"])

        if st.button("Çevir"):
            try:
                result = amount * row[from_currency] / row[to_currency]
                st.success(f"{amount} {from_currency} = {result:.2f} {to_currency}")
            except:
                st.error("Çeviri yapılamadı.")
    else:
        st.warning("Seçilen tarihe ait veri bulunamadı.")

    
    if st.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()
