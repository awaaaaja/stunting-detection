"""Rule-based recommendation fallback untuk sistem deteksi stunting.

Digunakan saat RAG tidak tersedia atau gagal retrieve chunk relevan.
Berdasarkan PNPK Stunting (Kepmenkes 1928/2022) dan Permenkes 2/2020.
"""
from typing import Optional

REKOMENDASI = {
    "severely stunted": {
        "ringkasan": (
            "Balita terindikasi severely stunted. Risiko tinggi memerlukan penanganan segera. "
            "Rujuk ke Puskesmas atau Fasilitas Kesehatan Rujukan untuk tata laksana lanjutan."
        ),
        "poin": [
            "Segera rujuk ke Puskesmas atau Rumah Sakit untuk evaluasi medis lengkap",
            "Lakukan anamnesis riwayat penyakit penyerta (infeksi berulang, TB, kelainan kongenital)",
            "Berikan PMT Pemulihan (Pangan Olahan untuk Keperluan Medis Khusus/PKAK) sesuai indikasi",
            "Konseling ASI eksklusif (jika usia <6 bulan) atau MPASI tinggi protein hewani (jika usia >=6 bulan)",
            "Evaluasi kepatuhan imunisasi dan suplementasi vitamin A, zat besi, zink",
            "Lakukan stimulasi tumbuh kembang sesuai usia",
            "Pantau berat badan setiap minggu dan tinggi badan setiap bulan",
            "Cari faktor risiko lingkungan: sanitasi, air bersih, asap rokok",
            "Konseling pola asuh dan stimulasi psikososial kepada orang tua",
            "Jadwalkan kunjungan ulang dalam 2 minggu untuk evaluasi",
        ],
        "sumber": ["PNPK Tata Laksana Stunting (Kepmenkes 1928/2022)", "Permenkes No. 2/2020 tentang Standar Antropometri"],
    },
    "stunted": {
        "ringkasan": (
            "Balita terindikasi stunted. Diperlukan intervensi gizi dan pemantauan rutin "
            "untuk mencegah perburukan status gizi."
        ),
        "poin": [
            "Berikan PMT (Pemberian Makanan Tambahan) tinggi protein hewani: telur, ikan, susu, hati ayam",
            "Konseling ASI eksklusif sampai usia 6 bulan",
            "Edukasi MPASI tepat waktu, adekuat, aman, dan diberikan dengan responsif",
            "Suplementasi vitamin A (setiap Februari dan Agustus) dan taburia (zat besi + zink)",
            "Pastikan imunisasi dasar lengkap sesuai usia",
            "Aktifkan partisipasi di Posyandu setiap bulan untuk pemantauan pertumbuhan",
            "Konseling pola asuh: stimulasi, kebersihan, dan pengasuhan responsif",
            "Evaluasi sanitasi lingkungan: akses air bersih, jamban sehat, CTPS",
            "Jika tidak ada perbaikan dalam 3 bulan, rujuk ke Puskesmas",
            "Pantau tinggi dan berat badan setiap bulan di Posyandu",
        ],
        "sumber": ["PNPK Tata Laksana Stunting (Kepmenkes 1928/2022)", "Permenkes No. 2/2020"],
    },
    "normal": {
        "ringkasan": (
            "Balita dalam status gizi normal. Pertahankan pola asuh dan gizi yang baik "
            "untuk mencegah stunting."
        ),
        "poin": [
            "Pertahankan pola makan bergizi seimbang sesuai usia",
            "Lanjutkan ASI eksklusif sampai usia 6 bulan, lanjutkan ASI sampai 2 tahun",
            "MPASI bergizi tinggi protein hewani mulai usia 6 bulan",
            "Pantau pertumbuhan rutin setiap bulan di Posyandu",
            "Lengkapi imunisasi dasar sesuai jadwal",
            "Suplementasi vitamin A rutin setiap Februari dan Agustus",
            "Terapkan Perilaku Hidup Bersih dan Sehat (PHBS)",
            "Stimulasi tumbuh kembang sesuai usia: ajak bicara, bermain, dan berinteraksi",
            "Pantau tanda bahaya: berat badan tidak naik, nafsu makan menurun, sakit berulang",
            "Jika ada perubahan pola pertumbuhan, segera konsultasi ke Posyandu",
        ],
        "sumber": ["Permenkes No. 2/2020", "Pedoman Gizi Seimbang Kemenkes RI"],
    },
    "tinggi": {
        "ringkasan": (
            "Balita memiliki tinggi di atas standar. Pantau pertumbuhan secara rutin "
            "dan pastikan tidak ada faktor risiko obesitas."
        ),
        "poin": [
            "Tetap pantau pertumbuhan setiap bulan di Posyandu",
            "Pastikan pola makan sesuai kebutuhan, jangan berlebihan",
            "Batasi konsumsi gula, garam, dan lemak berlebih",
            "Aktivitas fisik sesuai usia: merangkak, berjalan, bermain aktif",
            "Evaluasi potensi obesitas jika berat badan tidak proporsional",
            "Lanjutkan ASI/MPASI sesuai panduan",
            "Konsultasi ke tenaga kesehatan jika kecepatan pertumbuhan melambat drastis",
            "Lengkapi imunisasi dan suplementasi vitamin sesuai jadwal",
        ],
        "sumber": ["Permenkes No. 2/2020", "Pedoman Gizi Seimbang Kemenkes RI"],
    },
}


def get_rekomendasi_rule(prediction_class: str, risk_score: float, feature_desc: str, usia: int) -> dict:
    """Generate structured recommendation from rules (no external dependencies)."""
    cls_key = prediction_class.lower().strip()
    template = REKOMENDASI.get(cls_key, REKOMENDASI["normal"])

    poin = template["poin"]
    ringkasan = template["ringkasan"]
    sumber = template["sumber"]

    # Tambahkan konteks spesifik
    if risk_score > 0.5:
        risk_ctx = "Risiko stunting tinggi."
    elif risk_score > 0:
        risk_ctx = "Risiko stunting ringan."
    else:
        risk_ctx = "Tidak ada risiko stunting."

    if usia < 6:
        usia_ctx = "Usia di bawah 6 bulan: fokus pada ASI eksklusif."
    elif usia < 24:
        usia_ctx = "Usia 6-24 bulan: periode kritis MPASI dan pertumbuhan cepat."
    else:
        usia_ctx = "Usia 24-60 bulan: intervensi gizi dan stimulasi lanjutan."

    poin_narasi = ". ".join(p.capitalize() for p in poin)

    answer = (
        "Analisis: %s %s Faktor dominan: %s. "
        "%s "
        "Rekomendasi penanganan: %s."
    ) % (
        risk_ctx,
        usia_ctx,
        feature_desc,
        ringkasan,
        poin_narasi,
    )

    return {
        "answer": answer,
        "sources": [{"source": s, "page": None} for s in sumber],
    }


def get_rekomendasi_hybrid(
    prediction_class: str,
    risk_score: float,
    feature_desc: str,
    usia: int,
    rag_result: Optional[dict],
) -> dict:
    """Hybrid: prefer RAG result, fallback to rule-based."""
    if rag_result is not None and rag_result.get("answer") and len(rag_result["answer"]) > 20:
        return rag_result

    return get_rekomendasi_rule(prediction_class, risk_score, feature_desc, usia)
