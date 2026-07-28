"""Build comprehensive clinical reference from web search + PNPK text + PDF."""
import os, json, re, requests, time
from pathlib import Path
import dotenv
dotenv.load_dotenv()

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "docs"
OUTPUT_FILE = Path(__file__).parent / "clinical_chunks.json"

all_chunks = []
seen_texts = set()

def add_chunk(text, source, page=1):
    text = text.strip()
    if len(text) < 100 or text.count(" ") < 10:
        return
    key = text[:100]
    if key in seen_texts:
        return
    seen_texts.add(key)
    all_chunks.append({"text": text, "source": source, "page": page})

def smart_split(text, source, page=1, max_chars=500):
    """Split a long text into chunks at sentence/paragraph boundaries."""
    paragraphs = re.split(r"\n\s*\n", text)
    buffer = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(buffer) + len(para) < max_chars:
            buffer += para + "\n\n"
        else:
            if buffer.strip():
                add_chunk(buffer.strip(), source, page)
            buffer = para + "\n\n"
    if buffer.strip():
        add_chunk(buffer.strip(), source, page)

# ================================================================
# 1. PNPK Text File — already on disk
# ================================================================
pnpk_text = DOCS_DIR / "pnpk_stunting_referensi.txt"
if pnpk_text.exists():
    text = pnpk_text.read_text(encoding="utf-8")
    # Split by BAB
    sections = re.split(r"(?=BAB\s+[IVX]+)", text)
    for i, sec in enumerate(sections):
        sec = sec.strip()
        if not sec:
            continue
        # Further split by numbered sub-sections like "1. ..." or "a. ..."
        subs = re.split(r"\n(?=\d+\.\s+[A-Z]|[a-z]\.\s+[A-Z])", sec)
        for sub in subs:
            sub = sub.strip()
            if len(sub) > 100:
                smart_split(sub, "PNPK Stunting (Kepmenkes 1928/2022)", page=i+1)
    print(f"  PNPK text: {sum(1 for c in all_chunks if 'PNPK' in c['source'])} chunks")

# ================================================================
# 2. WHO 2023 Guideline — from web search results
# ================================================================
who_content = """
WHO Guideline on Prevention and Management of Wasting (2023)

KEY RECOMMENDATIONS FOR STUNTING MANAGEMENT:

1. All infants and children under 5 years presenting to primary health-care facilities should have both weight and length/height measured to classify nutritional status according to WHO child growth standards.

2. Caregivers of all children under 5 years should receive nutrition counselling including promotion of exclusive breastfeeding for first 6 months and continued breastfeeding until 24 months or beyond.

3. Supplementary foods for treating stunting (chronic undernutrition) among children at primary health-care facilities is NOT recommended as a routine intervention. The focus should be on nutrition counselling and addressing underlying causes.

4. Children with severe wasting should be triaged immediately. Those with danger signs need inpatient care. Those without complications can be managed as outpatients with RUTF.

5. For moderate wasting, children should have access to a nutrient-dense diet. Specially formulated foods (SFFs) like lipid-based nutrient supplements (LNS) are preferred when supplementation is needed.

6. Preventive interventions should use a multisectoral approach: food, health, WASH, social protection. Include access to healthy diets, nutrition counselling, breastfeeding promotion.

7. Continuity of care between inpatient and outpatient services is vital for follow-up of children with wasting.

SOURCE: WHO. WHO guideline on the prevention and management of wasting and nutritional oedema (acute malnutrition) in infants and children under 5 years. Geneva: World Health Organization; 2023.
"""
smart_split(who_content, "WHO Guideline 2023 — Wasting & Nutrition", page=1)

# ================================================================
# 3. WHO Stunting Brief (2024/2025)
# ================================================================
stunting_brief = """
WHO STUNTING BRIEF — KEY INTERVENTIONS (2024)

Stunting is linked with other global nutrition targets and can be substantially reduced with an intervention package delivered during preconception, pregnancy, and early childhood.

PRIORITY INTERVENTIONS:
1. Improve nutrition of adolescent girls and women before pregnancy
2. Ensure pregnant and lactating women are adequately nourished
3. Exclusive breastfeeding for first 6 months of life
4. Children aged 6-23 months consume adequate complementary foods in addition to breastmilk
5. Stronger food systems including food fortification and biofortification
6. Food assistance programs for vulnerable populations
7. Social protection policies for adolescent girls and women
8. Labour policies including maternity protection
9. Laws curtailing marketing of breast-milk substitutes

COMPLEMENTARY FEEDING PRIORITY ACTIONS:
1. Establish national complementary feeding guidelines
2. Stimulate production of nutritious local foods for young children
3. Deliver quality counselling through community health workers
4. Provide appropriate food supplements for vulnerable children
5. Set standards for safety and quality of commercial complementary foods
6. Implement WHO guidance on ending inappropriate marketing of foods for young children
7. Leverage social protection systems for vulnerable families
8. Enhance accountability through robust data systems

OPERATIONAL 2030 TARGETS:
- Increase proportion of children 6-23 months consuming minimum dietary diversity by 20%
- Increase proportion of caregivers counselled on infant and young child feeding by 65%

SOURCE: WHO Stunting Brief, 2024. https://iris.who.int/bitstreams/21efb9ee-58ee-481c-88c1-7bf5ef7b8cbc/content
"""
smart_split(stunting_brief, "WHO Stunting Brief 2024", page=1)

# ================================================================
# 4. PNPK Kemkes — Detailed Clinical Content from PDF Web Search
# ================================================================
pnpk_detailed = """
PNPK TATA LAKSANA STUNTING — KEPMENKES 1928/2022 (DETAILED)

DIAGNOSIS:
- Diagnosis stunting ditegakkan berdasarkan anamnesis, pemeriksaan fisik, pemeriksaan antropometri, dan pemeriksaan penunjang (Peringkat bukti 1, derajat rekomendasi A).
- Pengukuran antropometrik harus menggunakan teknik dan alat ukur standar. Anak <2 tahun: infantometer. Anak >=2 tahun: stadiometer.
- Pada setiap anak pendek harus dilakukan evaluasi: (a) bedakan varian normal vs patologis; (b) tentukan stunting atau bukan melalui laju pertumbuhan dan Potensi Tinggi Genetik (PTG).
- Pemeriksaan penunjang berdasarkan indikasi medis. Pemeriksaan usia tulang (bone age) pada anak >=2 tahun.
- Skrining TBC harus dilakukan pada semua anak stunting (Peringkat bukti 2, derajat rekomendasi A).

CLASSIFICATION (TB/U):
- Sangat pendek (severely stunted): TB/U < -3 SD
- Pendek (stunted): TB/U -2 SD s/d -3 SD
- Normal: TB/U -2 SD s/d +2 SD

PENCEGAHAN PRIMER (di Posyandu oleh Kader):
- Pemantauan pertumbuhan, pengukuran PB/TB dan BB setiap bulan
- Edukasi ASI eksklusif dan MPASI dengan protein hewani
- PMT mengandung protein hewani (telur, ayam, ikan, daging, susu)
- Jika TB/U <-2 SD atau weight faltering: rujuk ke FKTP/Puskesmas

PENCEGAHAN SEKUNDER (di Puskesmas oleh Dokter):
- Konfirmasi pengukuran antropometri
- Penelusuran penyebab potensial stunting
- Anak dengan BB rendah, weight faltering, gizi kurang (tapi TB/U >= -2 SD): dapat diberikan PDK (Pangan Diet Khusus)
- PDK: susu formula standar (0-12 bulan) atau susu pertumbuhan (1-3 tahun)
- PDK harus memenuhi: ijin BPOM, berbasis protein hewani, PER >10%, gula tambahan maksimal 10%
- Dosis PDK: 30% dari kebutuhan kalori, kontrol 2 minggu
- Pemeriksaan penunjang dasar: darah rutin, urinalisis, feses rutin, Mantoux
- Jika ada komplikasi (PJK, dll) atau tidak respon 1 minggu: rujuk ke dokter spesialis anak di FKRTL

PENCEGAHAN TERSIER (di RS oleh Dokter Spesialis Anak):
- Konfirmasi diagnosis stunting
- Anamnesis, fisik, penunjang untuk klasifikasi pendek (varian normal vs patologis, proporsional vs disproporsional)
- Penelusuran red flags
- Jika ditemukan penyebab potensial: tata laksana sesuai PNPK terkait

TATA LAKSANA GIZI:
- Tiga aspek: tata laksana nutrisi (PER 10-15%), aktivitas fisik 30-60 menit/3-5x seminggu, jadwal tidur teratur (tidur malam pukul 21.00 untuk deep sleep 23.00-03.00)
- Kebutuhan kalori: RDA/AKG berdasarkan berat badan ideal x RDA menurut height age
- Rute pemberian: oral (utama), enteral, parenteral
- Jenis makanan berdasarkan status gizi:
  * Stunting, tidak underweight: susu formula pertumbuhan dengan PER minimal 10%
  * Stunting underweight: PKMK 1 kkal/ml dengan PER minimal 10%
  * Stunting, gizi kurang: PKMK 1-1.5 kkal/ml dengan PER minimal 10%
- PKMK: Pangan Keperluan Medis Khusus, harus diresepkan dokter spesialis anak
- WHO: 10-15% energi dari protein untuk catch-up growth. Protein hewani memiliki DIAAS >=100.
- Pemberian lebih dari satu sumber protein hewani menurunkan kejadian stunting
- Pemantauan setiap 2 minggu: akseptabilitas, toleransi, efektivitas

SISTEM RUJUKAN BERJENJANG:
1. POSYANDU: Kader deteksi dini, ukur antropometri, PMT, edukasi. Jika stunting/weight faltering/growth deceleration -> rujuk ke FKTP
2. PUSKESMAS (FKTP): Dokter konfirmasi, cari penyebab, beri PDK, konseling. Jika ada penyebab penyerta -> rujuk ke dokter spesialis anak
3. RSUD (FKRTL): Dokter spesialis anak konfirmasi diagnosis, tata laksana nutrisi, edukasi feeding rules

EDUKASI GIZI BERDASARKAN USIA:
- Usia 6-8 bulan: 200 kkal, 15 gr protein, 30% protein hewani (4.5 gr). Contoh: 1 telur ayam
- Usia 9-11 bulan: 300 kkal, 15 gr protein, 50% protein hewani (7.5 gr). Contoh: 1 telur + 1/2 hati ayam
- Usia 12-24 bulan: 550 kkal, 20 gr protein, 70% protein hewani (14 gr). Contoh: 1 telur + 30 gr ikan + 1 susu UHT
- Usia 24-60 bulan: 1400 kkal, 20 gr protein, 100% protein hewani (25 gr). Contoh: 2 telur + 1 hati ayam + 2 susu UHT

FEEDING RULES (contoh jadwal untuk 6-11 bulan dengan weight faltering):
- 06.00: ASI (15-30 menit) atau ASI perah 150 ml
- 08.00: Makan pagi + protein hewani
- 10.00: PDK 5 takar (150 ml) PER >10%
- 12.00: Makan siang + protein hewani
- 14.00: ASI perah 150 ml atau PDK 5 takar
- 16.00: PDK 5 takar (150 ml) PER >10%
- 18.00: Makan malam + protein hewani
- 20.00: ASI langsung atau ASI perah 150 ml

SOURCE: Keputusan Menteri Kesehatan HK.01.07/MENKES/1928/2022 tentang PNPK Tata Laksana Stunting
"""
smart_split(pnpk_detailed, "PNPK Stunting Detail (Kepmenkes 1928/2022)", page=2)

# ================================================================
# 5. PMT Local Technical Guidelines (Kemkes 2025)
# ================================================================
pmt_content = """
PETUNJUK TEKNIS PMT LOKAL — KEMENKES 2025

SASARAN PMT LOKAL:
- Balita berat badan tidak naik (1T)
- Balita berat badan kurang
- Balita gizi kurang
- Dengan atau tanpa stunting

ALUR TATA LAKSANA BALITA STUNTING:
1. Jika ditemukan balita stunting -> rujuk ke Puskesmas untuk konfirmasi status gizi
2. Jika disertai masalah gizi akut -> tata laksana dengan PMT berbahan pangan lokal sesuai masalah gizi akut
3. Setelah selesai 1 siklus PMT lokal -> rujuk ke RS untuk tata laksana stunting
4. Balita stunting dengan gizi akut: rujuk setelah selesai 1 siklus PMT lokal
5. Jika BB naik adekuat dan balita tidak stunting -> tata laksana selesai
6. Jika BB naik adekuat tapi balita masih stunting -> rujuk ke RS setelah 1 siklus PMT lokal

KETENTUAN PMT LOKAL:
- Minimal 80% untuk belanja bahan makanan
- Maksimal 20% untuk penyelenggaraan (upah memasak, distribusi, manajemen)
- Gizi buruk BUKAN sasaran PMT lokal -> tata laksana gizi buruk mengacu pedoman tersendiri

SOURCE: Kepdirjenkesprimkom No. 576/2025 tentang Petunjuk Teknis PMT Lokal
"""
smart_split(pmt_content, "Juknis PMT Lokal Kemkes 2025", page=1)

# ================================================================
# 6. IDAI & IPC Guidelines for Puskesmas
# ================================================================
ipc_content = """
INTERPROFESSIONAL COLLABORATION FOR STUNTING MANAGEMENT AT PUSKESMAS — EXPERT CONSENSUS 2024

KEY CONSENSUS:
1. Accelerating stunting reduction must focus on life cycle, especially first 1000 days of life
2. Risk identification and preventive interventions should be done pre-pregnancy and during pregnancy
3. Weighing and screening conducted during under-five years period
4. Prioritize screening and management of toddlers with nutritional problems
5. Stunting addressed from upstream to downstream: promotive, preventive, treatment, rehabilitative

ROLES:
- DOCTOR: Diagnosis, treatment, referral decision, medical management
- NURSE: Assessment, care planning, referrals, health education, counselling
- NUTRITIONIST: Nutritional assessment, dietary planning, counselling on feeding
- MIDWIFE: Maternal and child health monitoring, breastfeeding support
- PUBLIC HEALTH SPECIALIST: Surveillance, data analysis, community empowerment, advocacy

IMPLEMENTATION STEPS:
1. Socialize guidelines to Puskesmas heads (94% consensus)
2. Socialize among professional organizations involved in stunting reduction
3. Organize interprofessional collaboration training for health workers (91% consensus)

SOURCE: Expert Consensus on IPC Guidelines on Stunting Management in Indonesian Primary Healthcare. Open Public Health Journal, 2024.
"""
smart_split(ipc_content, "IPC Guidelines Stunting Puskesmas 2024", page=1)

# ================================================================
# 7. Intervensi Stunting Terintegrasi (Pedoman Kemkes)
# ================================================================
intervensi_content = """
PEDOMAN INTERVENSI PENURUNAN STUNTING TERINTEGRASI

KERANGKA KONSEPTUAL:
- Intervensi Gizi Spesifik: mengatasi penyebab langsung (asupan makanan, infeksi)
- Intervensi Gizi Sensitif: mengatasi penyebab tidak langsung (ketahanan pangan, sanitasi, akses kesehatan)
- Prasyarat pendukung: komitmen politik, lintas sektor, kapasitas pelaksana

INTERVENSI GIZI SPESIFIK PRIORITAS:
1. ASI eksklusif 6 bulan
2. MPASI kaya protein hewani mulai 6 bulan
3. Suplementasi vitamin A (Februari dan Agustus)
4. Suplementasi zat besi dan zink (taburia)
5. Imunisasi dasar lengkap
6. Pemantauan pertumbuhan bulanan di Posyandu
7. PMT untuk balita gizi kurang
8. Tatalaksana gizi buruk

TARGET INDIKATOR UTAMA:
1. Prevalensi stunting pada baduta dan balita
2. Presentase BBLR
3. Prevalensi underweight pada balita
4. Prevalensi wasting pada balita
5. Presentase ASI eksklusif <6 bulan
6. Prevalensi anemia pada ibu hamil dan rematri
7. Prevalensi kecacingan pada balita
8. Prevalensi diare pada baduta dan balita

PENDEKATAN: Holistik, Integratif, Tematik, dan Spatial (HITS)
Lokasi fokus: 160 kabupaten/kota prioritas

SOURCE: Pedoman Pelaksanaan Intervensi Penurunan Stunting Terintegrasi di Kabupaten/Kota. Kemkes, 2018 (diperbarui).
"""
smart_split(intervensi_content, "Pedoman Intervensi Stunting Terintegrasi", page=1)

# ================================================================
# Save all chunks
# ================================================================
print(f"\n=== Total clinical chunks: {len(all_chunks)} ===")
source_counts = {}
for c in all_chunks:
    s = c["source"]
    source_counts[s] = source_counts.get(s, 0) + 1
for s, count in sorted(source_counts.items()):
    print(f"  {s}: {count}")

OUTPUT_FILE.write_text(json.dumps(all_chunks, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nSaved to {OUTPUT_FILE.name}")

# Show samples
print("\n=== Sample chunks ===")
for i, c in enumerate(all_chunks[:3]):
    print(f"\n--- Chunk {i+1} ({c['source']}) ---")
    print(c["text"][:200])
    print("...")
