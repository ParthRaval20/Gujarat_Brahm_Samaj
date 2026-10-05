"""
Seed 100 unique members with distinct names, occupations, educational qualifications,
and family members for Gujarat Brahm Samaj database.
"""

from __future__ import annotations
import sys
import os
from datetime import datetime, date

# Ensure root workspace is on python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from database.connection import get_session, init_db
from database.models import Member, FamilyMember, AppSetting
from services.search_service import SearchService


MEMBERS_DATA = [
    {
        "code_num": 1,
        "first_name": "પરેશકુમાર", "father_name": "હિંમતલાલ", "surname": "રાવલ",
        "mobile": "9825010001", "landline": "079-26581001", "email": "paresh.raval@gmail.com",
        "address": "૪૨, શિવમ બંગલોઝ, ડ્રાઈવ-ઈન રોડ", "village_address": "ઈડર, જિ. સાબરકાંઠા",
        "city": "અમદાવાદ", "district": "અમદાવાદ", "state": "Gujarat", "pincode": "380054",
        "occupation": "સોફ્ટવેર એન્જિનિયર (Software Engineer)",
        "business_address": "ઇન્ફોસિટી, બ્લોક-સી, ગાંધીનગર",
        "income": "₹ 1,20,000 / માસિક",
        "education": "B.E. Computer Engineering (L.D. College)",
        "blood_group": "B+", "samaj": "શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ", "fee": "આજીવન (Life Member)",
        "birth_date": "1985-06-14",
        "family": [
            {"name": "ભાવનાબેન પરેશકુમાર રાવલ", "relation": "પત્ની (Wife)", "age": 38, "education": "M.Sc. Organic Chemistry", "occupation": "શિક્ષિકા (Teacher)", "blood_group": "B+", "contact": "9825020001"},
            {"name": "આરવ પરેશકુમાર રાવલ", "relation": "પુત્ર (Son)", "age": 14, "education": "ધોરણ ૯ (English Medium)", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "O+", "contact": ""},
            {"name": "અનન્યા પરેશકુમાર રાવલ", "relation": "પુત્રી (Daughter)", "age": 10, "education": "ધોરણ ૫ (Primary)", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "B+", "contact": ""}
        ]
    },
    {
        "code_num": 2,
        "first_name": "મહેશભાઈ", "father_name": "કાંતિલાલ", "surname": "જોશી",
        "mobile": "9825010002", "landline": "02772-241002", "email": "mahesh.joshi@gmail.com",
        "address": "૧૫, ગાયત્રી સોસાયટી, મહાવીરનગર", "village_address": "પ્રાંતિજ, સાબરકાંઠા",
        "city": "હિંમતનગર", "district": "સાબરકાંઠા", "state": "Gujarat", "pincode": "383001",
        "occupation": "મુખ્ય શાળા આચાર્ય (School Principal)",
        "business_address": "સરકારી ઉચ્ચતર માધ્યમિક શાળા, હિંમતનગર",
        "income": "₹ 85,000 / માસિક",
        "education": "M.A., B.Ed, M.Ed (Sanskrit)",
        "blood_group": "A+", "samaj": "ઔદીચ્ય સહસ્ત્ર બ્રહ્મ સમાજ", "fee": "₹ 1000",
        "birth_date": "1972-04-18",
        "family": [
            {"name": "ગીતાબેન મહેશભાઈ જોશી", "relation": "પત્ની (Wife)", "age": 49, "education": "B.A. Gujarati", "occupation": "ગૃહિણી (Housewife)", "blood_group": "A+", "contact": "9825020002"},
            {"name": "ધ્રુવ મહેશભાઈ જોશી", "relation": "પુત્ર (Son)", "age": 22, "education": "B.Tech Mechanical", "occupation": "એન્જિનિયર (Engineer)", "blood_group": "A+", "contact": "9825030002"},
            {"name": "કાંતિલાલ ગોવિંદરામ જોશી", "relation": "પિતા (Father)", "age": 76, "education": "મેટ્રિક (Old SSC)", "occupation": "નિવૃત્ત (Retired)", "blood_group": "O+", "contact": ""}
        ]
    },
    {
        "code_num": 3,
        "first_name": "ભાવેશકુમાર", "father_name": "રતિલાલ", "surname": "વ્યાસ",
        "mobile": "9825010003", "landline": "0265-2341003", "email": "dr.bhavesh.vyas@gmail.com",
        "address": "૭, અલકાપુરી સોસાયટી, જેતલપુર રોડ", "village_address": "સિદ્ધપુર, જિ. પાટણ",
        "city": "વડોદરા", "district": "વડોદરા", "state": "Gujarat", "pincode": "390007",
        "occupation": "એમ.ડી. ફિઝિશિયન તબીબ (MD Physician Doctor)",
        "business_address": "વ્યાસ ક્લિનિક અને હોસ્પિટલ, રાવપુરા, વડોદરા",
        "income": "₹ 2,50,000 / માસિક",
        "education": "M.B.B.S., M.D. (Internal Medicine)",
        "blood_group": "O+", "samaj": "સિદ્ધપુરા ઔદીચ્ય બ્રહ્મ સમાજ", "fee": "આજીવન (Life Member)",
        "birth_date": "1978-11-25",
        "family": [
            {"name": "ડો. સ્નેહા ભાવેશકુમાર વ્યાસ", "relation": "પત્ની (Wife)", "age": 44, "education": "M.B.B.S., D.G.O. (Gynecologist)", "occupation": "ડોક્ટર (Doctor)", "blood_group": "O+", "contact": "9825020003"},
            {"name": "આદિત્ય ભાવેશ વ્યાસ", "relation": "પુત્ર (Son)", "age": 18, "education": "ધોરણ ૧૨ સાયન્સ (NEET Aspirant)", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "O+", "contact": "9825030003"}
        ]
    },
    {
        "code_num": 4,
        "first_name": "પાર્થભાઈ", "father_name": "જગદીશચંદ્ર", "surname": "ભટ્ટ",
        "mobile": "9825010004", "landline": "", "email": "ca.parth.bhatt@gmail.com",
        "address": "૧૦૪, સમર્થ એપાર્ટમેન્ટ, અડાજણ રોડ", "village_address": "તલોદ, જિ. સાબરકાંઠા",
        "city": "સુરત", "district": "સુરત", "state": "Gujarat", "pincode": "395009",
        "occupation": "ચાર્ટર્ડ એકાઉન્ટન્ટ (Chartered Accountant - CA)",
        "business_address": "ભટ્ટ એન્ડ એસોસિએટ્સ, રીંગ રોડ, સુરત",
        "income": "₹ 1,80,000 / માસિક",
        "education": "Chartered Accountant (FCA), B.Com",
        "blood_group": "AB+", "samaj": "શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ", "fee": "આજીવન (Life Member)",
        "birth_date": "1988-03-09",
        "family": [
            {"name": "પ્રિયા પાર્થ ભટ્ટ", "relation": "પત્ની (Wife)", "age": 34, "education": "M.Com, Inter CA", "occupation": "ટેક્સ એનાલિસ્ટ (Tax Analyst)", "blood_group": "AB+", "contact": "9825020004"},
            {"name": "કિયા પાર્થ ભટ્ટ", "relation": "પુત્રી (Daughter)", "age": 6, "education": "ધોરણ ૧ (Primary)", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "A+", "contact": ""}
        ]
    },
    {
        "code_num": 5,
        "first_name": "સંજયકુમાર", "father_name": "મનહરલાલ", "surname": "શુક્લ",
        "mobile": "9825010005", "landline": "0281-2451005", "email": "adv.sanjay.shukla@yahoo.com",
        "address": "૨૮, શારદાનગર, કાલાવડ રોડ", "village_address": "વડનગર, જિ. મહેસાણા",
        "city": "રાજકોટ", "district": "રાજકોટ", "state": "Gujarat", "pincode": "360005",
        "occupation": "હાઈકોર્ટ વકીલ / એડવોકેટ (High Court Advocate)",
        "business_address": "ડિસ્ટ્રિક્ટ કોર્ટ ચેમ્બર્સ, યાજ્ઞિક રોડ, રાજકોટ",
        "income": "₹ 1,40,000 / માસિક",
        "education": "B.Com, LL.B., LL.M. (Constitutional Law)",
        "blood_group": "B-", "samaj": "ખેડાવળ બ્રહ્મ સમાજ", "fee": "₹ 1000",
        "birth_date": "1975-09-12",
        "family": [
            {"name": "રેખાબેન સંજયકુમાર શુક્લ", "relation": "પત્ની (Wife)", "age": 46, "education": "M.A. History", "occupation": "ગૃહિણી (Housewife)", "blood_group": "B-", "contact": "9825020005"},
            {"name": "રોહન સંજય શુક્લ", "relation": "પુત્ર (Son)", "age": 20, "education": "B.A. LL.B. (5 Year Law)", "occupation": "વિદ્યાર્થી (Law Student)", "blood_group": "B+", "contact": "9825030005"}
        ]
    },
    {
        "code_num": 6,
        "first_name": "દર્શનભાઈ", "father_name": "ચંદ્રકાંત", "surname": "દવે",
        "mobile": "9825010006", "landline": "079-23241006", "email": "darshan.dave@gmail.com",
        "address": "૫૦૩, સેક્ટર-૨૧, ગાંધીનગર", "village_address": "મોડાસા, અરવલ્લી",
        "city": "ગાંધીનગર", "district": "ગાંધીનગર", "state": "Gujarat", "pincode": "382021",
        "occupation": "સિવિલ એન્જિનિયર અને કન્સલ્ટન્ટ (Civil Engineer & Consultant)",
        "business_address": "દવે કન્સલ્ટન્ટ્સ, સી.જી. રોડ, અમદાવાદ",
        "income": "₹ 1,60,000 / માસિક",
        "education": "B.E. Civil, M.Tech Structural Engineering",
        "blood_group": "O-", "samaj": "પ્રશ્નોરા નાગર બ્રહ્મ સમાજ", "fee": "આજીવન (Life Member)",
        "birth_date": "1983-01-30",
        "family": [
            {"name": "નીતા દર્શન દવે", "relation": "પત્ની (Wife)", "age": 39, "education": "B.Arch (Architecture)", "occupation": "ઇન્ટિરિયર ડિઝાઇનર (Interior Designer)", "blood_group": "O-", "contact": "9825020006"},
            {"name": "મિહીર દર્શન દવે", "relation": "પુત્ર (Son)", "age": 12, "education": "ધોરણ ૭ (English Medium)", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "O+", "contact": ""}
        ]
    },
    {
        "code_num": 7,
        "first_name": "જીતેન્દ્રકુમાર", "father_name": "નવનીતલાલ", "surname": "ત્રિવેદી",
        "mobile": "9825010007", "landline": "0278-2511007", "email": "jitu.trivedi@sbi.co.in",
        "address": "૧૪, સુભાષનગર, વાઘાવાડી રોડ", "village_address": "વિજયનગર, સાબરકાંઠા",
        "city": "ભાવનગર", "district": "ભાવનગર", "state": "Gujarat", "pincode": "364002",
        "occupation": "બેંક બ્રાન્ચ મેનેજર (Bank Branch Manager)",
        "business_address": "સ્ટેટ બેંક ઓફ ઇન્ડિયા, મેઇન બ્રાન્ચ, ભાવનગર",
        "income": "₹ 95,000 / માસિક",
        "education": "MBA (Banking & Finance), CAIIB",
        "blood_group": "A-", "samaj": "મોઢ બ્રહ્મ સમાજ", "fee": "₹ 500",
        "birth_date": "1980-07-22",
        "family": [
            {"name": "વર્ષાબેન જીતેન્દ્ર ત્રિવેદી", "relation": "પત્ની (Wife)", "age": 42, "education": "B.Com", "occupation": "ગૃહિણી (Housewife)", "blood_group": "A+", "contact": "9825020007"},
            {"name": "યશવી જીતેન્દ્ર ત્રિવેદી", "relation": "પુત્રી (Daughter)", "age": 16, "education": "ધોરણ ૧૧ કોમર્સ", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "A-", "contact": ""}
        ]
    },
    {
        "code_num": 8,
        "first_name": "હિતેશભાઈ", "father_name": "રમણલાલ", "surname": "જાની",
        "mobile": "9825010008", "landline": "0288-2671008", "email": "dr.hitesh.jani@gmail.com",
        "address": "૮૯, ગોકુલનગર, બેડી બંદર રોડ", "village_address": "ખેડબ્રહ્મા, સાબરકાંઠા",
        "city": "જામનગર", "district": "જામનગર", "state": "Gujarat", "pincode": "361008",
        "occupation": "પ્રોફેસર - ભૌતિકશાસ્ત્ર (Professor of Physics)",
        "business_address": "ડી.કે.વી. સાયન્સ કોલેજ, જામનગર",
        "income": "₹ 1,15,000 / માસિક",
        "education": "M.Sc. Physics, Ph.D. (Nanotechnology)",
        "blood_group": "AB-", "samaj": "ઝાલાવાડી ઔદીચ્ય બ્રહ્મ સમાજ", "fee": "આજીવન (Life Member)",
        "birth_date": "1976-12-05",
        "family": [
            {"name": "અલ્પાબેન હિતેશ જાની", "relation": "પત્ની (Wife)", "age": 45, "education": "M.Sc. Botany", "occupation": "લેક્ચરર (Lecturer)", "blood_group": "AB-", "contact": "9825020008"},
            {"name": "કેવલ હિતેશ જાની", "relation": "પુત્ર (Son)", "age": 19, "education": "B.Sc. Chemistry", "occupation": "વિદ્યાર્થી (College Student)", "blood_group": "B+", "contact": "9825030008"}
        ]
    },
    {
        "code_num": 9,
        "first_name": "નિલેશકુમાર", "father_name": "ભાનુપ્રસાદ", "surname": "ઉપાધ્યાય",
        "mobile": "9825010009", "landline": "0285-2621009", "email": "nilesh.pharm@gmail.com",
        "address": "૩૩, શાંતિનગર, જોષીપુરા", "village_address": "ભિલોડા, અરવલ્લી",
        "city": "જૂનાગઢ", "district": "જૂનાગઢ", "state": "Gujarat", "pincode": "362002",
        "occupation": "રજિસ્ટર્ડ ફાર્માસિસ્ટ (Registered Pharmacist)",
        "business_address": "સંજીવની મેડિકલ સ્ટોર, સ્ટેશન રોડ, જૂનાગઢ",
        "income": "₹ 70,000 / માસિક",
        "education": "B.Pharm, M.Pharm (Pharmaceutics)",
        "blood_group": "O+", "samaj": "સાંચોરા બ્રહ્મ સમાજ", "fee": "₹ 1000",
        "birth_date": "1982-05-17",
        "family": [
            {"name": "કલ્પના નિલેશ ઉપાધ્યાય", "relation": "પત્ની (Wife)", "age": 39, "education": "D.Pharm", "occupation": "ફાર્માસિસ્ટ સહાયક (Pharmacy Assistant)", "blood_group": "O+", "contact": "9825020009"},
            {"name": "હર્ષિલ નિલેશ ઉપાધ્યાય", "relation": "પુત્ર (Son)", "age": 13, "education": "ધોરણ ૮", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "A+", "contact": ""}
        ]
    },
    {
        "code_num": 10,
        "first_name": "પિયુષભાઈ", "father_name": "જયંતિલાલ", "surname": "મહેતા",
        "mobile": "9825010010", "landline": "02762-251010", "email": "piyush.arch@gmail.com",
        "address": "૫, યોગીનગર, રાધનપુર રોડ", "village_address": "વડનગર, મહેસાણા",
        "city": "મહેસાણા", "district": "મહેસાણા", "state": "Gujarat", "pincode": "384002",
        "occupation": "આર્કિટેક્ટ અને ઇન્ટિરિયર ડિઝાઇનર (Architect & Interior Designer)",
        "business_address": "મેહતા ક્રિએટિવ સ્ટુડિયો, ટી.બી. રોડ, મહેસાણા",
        "income": "₹ 1,50,000 / માસિક",
        "education": "B.Arch, Master of Urban Planning (CEPT)",
        "blood_group": "B+", "samaj": "નાગર બ્રહ્મ સમાજ", "fee": "આજીવન (Life Member)",
        "birth_date": "1984-08-11",
        "family": [
            {"name": "રૂપલ પિયુષ મહેતા", "relation": "પત્ની (Wife)", "age": 37, "education": "B.F.A. Fine Arts", "occupation": "ગ્રાફિક ડિઝાઇનર (Graphic Designer)", "blood_group": "B+", "contact": "9825020010"},
            {"name": "અન્વી પિયુષ મહેતા", "relation": "પુત્રી (Daughter)", "age": 8, "education": "ધોરણ ૩", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "B+", "contact": ""}
        ]
    },
    {
        "code_num": 11,
        "first_name": "કમલેશકુમાર", "father_name": "ગૌરીશંકર", "surname": "શાસ્ત્રી",
        "mobile": "9825010011", "landline": "02667-221011", "email": "shastri.kamlesh@gmail.com",
        "address": "જૂની ભાગોળ, શિવ મંદિર પાસે", "village_address": "સિદ્ધપુર પાટણ",
        "city": "પાટણ", "district": "પાટણ", "state": "Gujarat", "pincode": "384265",
        "occupation": "જ્યોતિષાચાર્ય અને કર્મકાંડી બ્રાહ્મણ (Astrologer & Vedic Priest)",
        "business_address": "શાસ્ત્રી જ્યોતિષ કાર્યાલય, સિદ્ધપુર",
        "income": "₹ 65,000 / માસિક",
        "education": "શાસ્ત્રી, આચાર્ય (વેદાંત અને કર્મકાંડ - સંપૂર્ણાનંદ સંસ્કૃત યુનિ.)",
        "blood_group": "A+", "samaj": "સિદ્ધપુરા ઔદીચ્ય બ્રહ્મ સમાજ", "fee": "₹ 500",
        "birth_date": "1970-10-03",
        "family": [
            {"name": "હંસાબેન કમલેશકુમાર શાસ્ત્રી", "relation": "પત્ની (Wife)", "age": 52, "education": "મેટ્રિક (10th)", "occupation": "ગૃહિણી (Housewife)", "blood_group": "A+", "contact": "9825020011"},
            {"name": "વેદાંત કમલેશ શાસ્ત્રી", "relation": "પુત્ર (Son)", "age": 24, "education": "શાસ્ત્રી (Sanskrit)", "occupation": "કર્મકાંડ સહાયક (Purohit)", "blood_group": "A+", "contact": "9825030011"}
        ]
    },
    {
        "code_num": 12,
        "first_name": "વિપુલભાઈ", "father_name": "ધનશંકર", "surname": "પંડ્યા",
        "mobile": "9825010012", "landline": "02742-251012", "email": "vipul.pandya.gas@gujarat.gov.in",
        "address": "બી-૧૨, સરકારી ઓફિસર્સ કોલોની", "village_address": "પાલનપુર, બનાસકાંઠા",
        "city": "પાલનપુર", "district": "બનાસકાંઠા", "state": "Gujarat", "pincode": "385001",
        "occupation": "ક્લાસ-૧ સરકારી અધિકારી (Class-1 Govt Officer / GAS)",
        "business_address": "કલેક્ટર કચેરી, જોરાવર પેલેસ, પાલનપુર",
        "income": "₹ 1,35,000 / માસિક",
        "education": "M.A. Public Administration, GPSC Class-1",
        "blood_group": "O+", "samaj": "રાજગોર બ્રહ્મ સમાજ", "fee": "આજીવન (Life Member)",
        "birth_date": "1979-02-14",
        "family": [
            {"name": "મીનાબેન વિપુલ પંડ્યા", "relation": "પત્ની (Wife)", "age": 43, "education": "M.A. Sociology", "occupation": "ગૃહિણી (Housewife)", "blood_group": "O+", "contact": "9825020012"},
            {"name": "પ્રિતેશ વિપુલ પંડ્યા", "relation": "પુત્ર (Son)", "age": 17, "education": "ધોરણ ૧૨ આર્ટ્સ", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "B+", "contact": "9825030012"}
        ]
    },
    {
        "code_num": 13,
        "first_name": "અશોકકુમાર", "father_name": "હરિલાલ", "surname": "દ્વિવેદી",
        "mobile": "9825010013", "landline": "0268-2521013", "email": "ashok.dwivedi@lt.com",
        "address": "૭૨, સૂર્યનગર, ડાકોર રોડ", "village_address": "નડિયાદ, ખેડા",
        "city": "નડિયાદ", "district": "ખેડા", "state": "Gujarat", "pincode": "387001",
        "occupation": "મિકેનિકલ ડિઝાઇન એન્જિનિયર (Mechanical Design Engineer)",
        "business_address": "એલ એન્ડ ટી નોલેજ સિટી, વડોદરા",
        "income": "₹ 1,10,000 / માસિક",
        "education": "B.E. Mechanical Engineering (DDU Nadiad)",
        "blood_group": "B+", "samaj": "ખેડાવળ બ્રહ્મ સમાજ", "fee": "₹ 1000",
        "birth_date": "1981-09-08",
        "family": [
            {"name": "નયનાબેન અશોક દ્વિવેદી", "relation": "પત્ની (Wife)", "age": 41, "education": "B.Sc. Mathematics", "occupation": "ગૃહિણી અને ટ્યુશન (Tutor)", "blood_group": "B+", "contact": "9825020013"},
            {"name": "કુંજલ અશોક દ્વિવેદી", "relation": "પુત્રી (Daughter)", "age": 15, "education": "ધોરણ ૧૦", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "O+", "contact": ""}
        ]
    },
    {
        "code_num": 14,
        "first_name": "મુકેશભાઈ", "father_name": "હરગોવિંદદાસ", "surname": "આચાર્ય",
        "mobile": "9825010014", "landline": "02692-231014", "email": "mukesh.acharya.media@gmail.com",
        "address": "૧૮, સરદાર ગંજ, વિદ્યાનગર રોડ", "village_address": "આણંદ, ચરોતર",
        "city": "આણંદ", "district": "આણંદ", "state": "Gujarat", "pincode": "388001",
        "occupation": "વરિષ્ઠ પત્રકાર અને તંત્રી (Senior Journalist & Editor)",
        "business_address": "દિવ્ય ચરોતર સાપ્તાહિક પ્રેસ, આણંદ",
        "income": "₹ 60,000 / માસિક",
        "education": "B.A. Journalism & Mass Communication",
        "blood_group": "AB+", "samaj": "શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ", "fee": "₹ 500",
        "birth_date": "1973-06-20",
        "family": [
            {"name": "પ્રતિમા મુકેશ આચાર્ય", "relation": "પત્ની (Wife)", "age": 48, "education": "B.A. Hindi", "occupation": "ગૃહિણી (Housewife)", "blood_group": "AB+", "contact": "9825020014"},
            {"name": "દેવ મુકેશ આચાર્ય", "relation": "પુત્ર (Son)", "age": 21, "education": "B.C.A. (Computer Applications)", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "A+", "contact": "9825030014"}
        ]
    },
    {
        "code_num": 15,
        "first_name": "રાજેશકુમાર", "father_name": "મંગળજી", "surname": "પુરોહિત",
        "mobile": "9825010015", "landline": "02642-241015", "email": "rajesh.purohit.elec@gmail.com",
        "address": "૫૪, નર્મદાનગર, ઝાડેશ્વર રોડ", "village_address": "અંકલેશ્વર, ભરૂચ",
        "city": "ભરૂચ", "district": "ભરૂચ", "state": "Gujarat", "pincode": "392001",
        "occupation": "ઇલેક્ટ્રિકલ કોન્ટ્રાક્ટર (Electrical Contractor)",
        "business_address": "પુરોહિત ઇલેક્ટ્રિકલ્સ, જીઆઈડીસી, અંકલેશ્વર",
        "income": "₹ 1,25,000 / માસિક",
        "education": "Diploma in Electrical Engineering (DEE)",
        "blood_group": "O+", "samaj": "બ્રહ્મભટ્ટ સમાજ", "fee": "આજીવન (Life Member)",
        "birth_date": "1986-10-10",
        "family": [
            {"name": "સંગીતા રાજેશ પુરોહિત", "relation": "પત્ની (Wife)", "age": 36, "education": "B.Com", "occupation": "એકાઉન્ટન્ટ (Accounts Manager)", "blood_group": "O+", "contact": "9825020015"},
            {"name": "આરુષ રાજેશ પુરોહિત", "relation": "પુત્ર (Son)", "age": 9, "education": "ધોરણ ૪", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "O+", "contact": ""}
        ]
    },
    {
        "code_num": 16,
        "first_name": "દિનેશભાઈ", "father_name": "બળવંતરાય", "surname": "નાગર",
        "mobile": "9825010016", "landline": "02637-231016", "email": "dinesh.nagar.tax@gmail.com",
        "address": "૨૧, શાંતિનિકેતન, લુન્સિકુઈ", "village_address": "નવસારી",
        "city": "નવસારી", "district": "નવસારી", "state": "Gujarat", "pincode": "396445",
        "occupation": "ટેક્સ કન્સલ્ટન્ટ અને જીએસટી નિષ્ણાત (Tax Consultant & GST Expert)",
        "business_address": "નાગર ટેક્સેશન સર્વિસ, સ્ટેશન રોડ, નવસારી",
        "income": "₹ 90,000 / માસિક",
        "education": "M.Com, Inter CA, Diploma in Taxation Practice (DTP)",
        "blood_group": "A+", "samaj": "નાગર બ્રહ્મ સમાજ", "fee": "₹ 1000",
        "birth_date": "1977-03-27",
        "family": [
            {"name": "તૃપ્તિ દિનેશ નાગર", "relation": "પત્ની (Wife)", "age": 44, "education": "M.A. English", "occupation": "શિક્ષિકા (English Teacher)", "blood_group": "A+", "contact": "9825020016"},
            {"name": "માનસી દિનેશ નાગર", "relation": "પુત્રી (Daughter)", "age": 18, "education": "ધોરણ ૧૨ કોમર્સ", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "B+", "contact": "9825030016"}
        ]
    },
    {
        "code_num": 17,
        "first_name": "સુરેશકુમાર", "father_name": "શંકરલાલ", "surname": "ખેડાવળ",
        "mobile": "9825010017", "landline": "02632-251017", "email": "suresh.data@gmail.com",
        "address": "૬૩, તિથલ રોડ, સંતોષી નગર", "village_address": "વલસાડ",
        "city": "વલસાડ", "district": "વલસાડ", "state": "Gujarat", "pincode": "396001",
        "occupation": "ડેટા સાયન્ટિસ્ટ અને એનાલિસ્ટ (Data Scientist & Analyst)",
        "business_address": "એક્સેન્ચર ટેક્નોલોજીસ, પૂણે (Remote)",
        "income": "₹ 1,75,000 / માસિક",
        "education": "M.Tech Data Science & AI (IIT Gandhinagar)",
        "blood_group": "B+", "samaj": "ખેડાવળ બ્રહ્મ સમાજ", "fee": "આજીવન (Life Member)",
        "birth_date": "1989-11-04",
        "family": [
            {"name": "વંદના સુરેશ ખેડાવળ", "relation": "પત્ની (Wife)", "age": 33, "education": "B.E. Computer", "occupation": "સોફ્ટવેર ડેવલપર (Software Developer)", "blood_group": "B+", "contact": "9825020017"},
            {"name": "વિહાન સુરેશ ખેડાવળ", "relation": "પુત્ર (Son)", "age": 4, "education": "નર્સરી (Kindergarten)", "occupation": "બાળક (Child)", "blood_group": "O+", "contact": ""}
        ]
    },
    {
        "code_num": 18,
        "first_name": "રમેશભાઈ", "father_name": "કેશવલાલ", "surname": "ઔદીચ્ય",
        "mobile": "9825010018", "landline": "02822-221018", "email": "dr.ramesh.ortho@gmail.com",
        "address": "૮, રવાપર રોડ, પટેલ સોસાયટી", "village_address": "મોરબી",
        "city": "મોરબી", "district": "મોરબી", "state": "Gujarat", "pincode": "363641",
        "occupation": "ઓર્થોપેડિક સર્જન (Orthopedic Surgeon)",
        "business_address": "શ્રીજી ઓર્થોપેડિક હોસ્પિટલ, શનાળા રોડ, મોરબી",
        "income": "₹ 3,20,000 / માસિક",
        "education": "M.B.B.S., M.S. (Orthopedics) (B.J. Medical)",
        "blood_group": "O+", "samaj": "ઔદીચ્ય સહસ્ત્ર બ્રહ્મ સમાજ", "fee": "આજીવન (Life Member)",
        "birth_date": "1974-08-16",
        "family": [
            {"name": "જાગૃતિ રમેશ ઔદીચ્ય", "relation": "પત્ની (Wife)", "age": 47, "education": "B.Sc. Nursing", "occupation": "હોસ્પિટલ એડમિનિસ્ટ્રેટર", "blood_group": "O+", "contact": "9825020018"},
            {"name": "ડો. અંકિત રમેશ ઔદીચ્ય", "relation": "પુત્ર (Son)", "age": 23, "education": "M.B.B.S. Intern", "occupation": "રેસિડેન્ટ ડોક્ટર (Doctor)", "blood_group": "A+", "contact": "9825030018"}
        ]
    },
    {
        "code_num": 19,
        "first_name": "હર્ષદકુમાર", "father_name": "પ્રતાપરાય", "surname": "મોઢ",
        "mobile": "9825010019", "landline": "0286-2241019", "email": "harshad.modh.math@gmail.com",
        "address": "૧૨, એમ.જી. રોડ, ચોપાટી પાસે", "village_address": "પોરબંદર",
        "city": "પોરબંદર", "district": "પોરબંદર", "state": "Gujarat", "pincode": "360575",
        "occupation": "ગણિતના અધ્યાપક (Mathematics Lecturer)",
        "business_address": "વી.આર.ટી.આઈ. કોલેજ, પોરબંદર",
        "income": "₹ 80,000 / માસિક",
        "education": "M.Sc. Mathematics, NET / SLET Qualified",
        "blood_group": "AB-", "samaj": "મોઢ બ્રહ્મ સમાજ", "fee": "₹ 500",
        "birth_date": "1980-01-21",
        "family": [
            {"name": "ચેતના હર્ષદકુમાર મોઢ", "relation": "પત્ની (Wife)", "age": 43, "education": "B.A., B.Ed", "occupation": "શિક્ષિકા (High School Teacher)", "blood_group": "AB-", "contact": "9825020019"},
            {"name": "પૂજન હર્ષદ મોઢ", "relation": "પુત્ર (Son)", "age": 16, "education": "ધોરણ ૧૧ સાયન્સ", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "B+", "contact": ""}
        ]
    },
    {
        "code_num": 20,
        "first_name": "પ્રતીકભાઈ", "father_name": "નટવરલાલ", "surname": "સિદ્ધપુરા",
        "mobile": "9825010020", "landline": "02772-231020", "email": "pratik.chem.res@gmail.com",
        "address": "૨૯, સહયોગ સોસાયટી, પોલો ગ્રાઉન્ડ રોડ", "village_address": "ઈડર, સાબરકાંઠા",
        "city": "હિંમતનગર", "district": "સાબરકાંઠા", "state": "Gujarat", "pincode": "383001",
        "occupation": "કેમિકલ રિસર્ચ સાયન્ટિસ્ટ (Chemical Research Scientist)",
        "business_address": "ઝાયડસ રિસર્ચ સેન્ટર, મોરૈયા, અમદાવાદ",
        "income": "₹ 1,45,000 / માસિક",
        "education": "M.Sc. Organic Chemistry, Ph.D. (Chemistry)",
        "blood_group": "A-", "samaj": "સિદ્ધપુરા ઔદીચ્ય બ્રહ્મ સમાજ", "fee": "આજીવન (Life Member)",
        "birth_date": "1987-04-12",
        "family": [
            {"name": "દીપ્તિ પ્રતીક સિદ્ધપુરા", "relation": "પત્ની (Wife)", "age": 35, "education": "M.Pharm (Quality Assurance)", "occupation": "ક્યુએ મેનેજર (QA Manager)", "blood_group": "A-", "contact": "9825020020"},
            {"name": "અવની પ્રતીક સિદ્ધપુરા", "relation": "પુત્રી (Daughter)", "age": 7, "education": "ધોરણ ૨", "occupation": "વિદ્યાર્થી (Student)", "blood_group": "O+", "contact": ""}
        ]
    }
]

# Function to generate remaining 80 members programmatically with rich authentic data
def generate_all_100_members():
    members = list(MEMBERS_DATA) # first 20 carefully handcrafted

    surnames = [
        "રાવલ", "જોશી", "વ્યાસ", "ભટ્ટ", "શુક્લ", "દવે", "ત્રિવેદી", "જાની",
        "ઉપાધ્યાય", "મહેતા", "શાસ્ત્રી", "પંડ્યા", "દ્વિવેદી", "આચાર્ય", "પુરોહિત",
        "નાગર", "ખેડાવળ", "ઔદીચ્ય", "મોઢ", "સિદ્ધપુરા", "સોમપુરા", "બ્રહ્મભટ્ટ",
        "ઠાકર", "પાઠક"
    ]

    first_names_m = [
        "મનનકુમાર", "ચિંતનભાઈ", "કેયુરકુમાર", "ધવલભાઈ", "ચેતનકુમાર", "અલ્પેશભાઈ",
        "મિલનકુમાર", "વિવેકભાઈ", "સૌરભકુમાર", "તુષારભાઈ", "જિજ્ઞેશકુમાર", "મયંકભાઈ",
        "સમીરકુમાર", "કૌશિકભાઈ", "પ્રશાંતકુમાર", "ગૌરાંગભાઈ", "દીપકકુમાર", "મનીષભાઈ",
        "અમિતકુમાર", "કાર્તિકભાઈ", "રોનકકુમાર", "પ્રણવભાઈ", "આનંદકુમાર", "યશભાઈ",
        "હિરેનકુમાર", "જયેશભાઈ", "અતુલકુમાર", "હરેશભાઈ", "કિરીટકુમાર", "પંકજભાઈ",
        "વિજયકુમાર", "પ્રકાશભાઈ", "ધર્મેશકુમાર", "નીતિનભાઈ", "ભાર્ગવકુમાર", "અંકુરભાઈ",
        "તન્મયકુમાર", "કલ્પેશભાઈ", "હાર્દિકકુમાર", "વિમલભાઈ", "દેવાંગકુમાર", "નરેન્દ્રભાઈ",
        "હેમંતકુમાર", "સંદીપભાઈ", "મનોજકુમાર", "ગિરીશભાઈ", "અરવિંદકુમાર", "જગદીશભાઈ",
        "શૈલેષકુમાર", "સુનિલભાઈ"
    ]

    first_names_f = [
        "ફાલ્ગુનીબેન", "હેમાબેન", "ઇલાબેન", "જ્યોતિબેન", "કોકિલાબેન", "માયાબેન",
        "નમ્રતાબેન", "પારુલબેન", "રશ્મિબેન", "શ્રદ્ધાબેન", "સ્વાતિબેન", "તારાબેન",
        "ઉમાબેન", "ભાવનાબેન", "કિરણબેન", "રીટાબેન", "શીલાબેન", "સુધાબેન",
        "દક્ષાબેન", "અનુરાધાબેન", "વૈશાલીબેન", "નિરુપમાબેન", "મંજુલાબેન", "શારદાબેન",
        "સરલાબેન", "પન્નાબેન", "અસ્મિતાબેન", "વૃંદાબેન", "રૂપાલબેન", "તેજલબેન"
    ]

    father_names = [
        "ચંદુલાલ", "પ્રમોદરાય", "ધીરજલાલ", "જયસુખલાલ", "ભોળાનાથ", "નારાયણદાસ",
        "બાલકૃષ્ણ", "વસંતરાય", "ગોવર્ધનભાઈ", "શિવશંકર", "નર્મદાશંકર", "હરિપ્રસાદ",
        "મનસુખલાલ", "નવલરામ", "છોટાલાલ", "અમૃતલાલ", "કનૈયાલાલ", "હરિશ્ચંદ્ર",
        "જગન્નાથ", "વિષ્ણુપ્રસાદ", "ગણેશલાલ", "ચતુરભાઈ", "લક્ષ્મીકાંત", "ઉમાકાંત",
        "ત્ર્યંબકલાલ", "રામચંદ્ર", "પ્રહલાદભાઈ", "મોહનલાલ", "દિગંતભાઈ", "ભવાનીશંકર"
    ]

    occupations_data = [
        # (Occupation string, Education string, Monthly Income string)
        ("ડેન્ટલ સર્જન / દંત ચિકિત્સક (Dental Surgeon / BDS)", "B.D.S., M.D.S. (Oral Surgery)", "₹ 1,70,000 / માસિક"),
        ("લાઈફ ઈન્સ્યોરન્સ ડેવલપમેન્ટ ઓફિસર (LIC Development Officer)", "B.Com, Licentiate (III)", "₹ 95,000 / માસિક"),
        ("ગ્રાફિક અને વેબ ડિઝાઇનર (Graphic & UI/UX Designer)", "B.Sc. IT, Advanced UI/UX Design", "₹ 75,000 / માસિક"),
        ("ક્લિનિકલ સાયકોલોજિસ્ટ (Clinical Psychologist)", "M.A. Clinical Psychology, RCI Certified", "₹ 85,000 / માસિક"),
        ("ઓટોમોબાઇલ શોરૂમ ઓનર (Automobile Business Owner)", "B.B.A. (Automobile Management)", "₹ 2,20,000 / માસિક"),
        ("સંસ્કૃત સાહિત્યના પ્રાધ્યાપક (Sanskrit Literature Professor)", "M.A. Sanskrit, Ph.D. (Gold Medalist)", "₹ 1,10,000 / માસિક"),
        ("આઈટી પ્રોજેક્ટ મેનેજર (IT Project Manager)", "B.Tech IT, PMP Certified (Scrum Master)", "₹ 2,10,000 / માસિક"),
        ("ગાયનેકોલોજિસ્ટ / સ્ત્રી રોગ નિષ્ણાત (Gynecologist - MD)", "M.B.B.S., D.G.O., M.D. (Gynecology)", "₹ 2,80,000 / માસિક"),
        ("ડિજિટલ માર્કેટિંગ સ્પેશિયાલિસ્ટ (Digital Marketing Specialist)", "B.B.A., MBA (Digital Marketing)", "₹ 80,000 / માસિક"),
        ("સહકારી બેંક આસિસ્ટન્ટ જનરલ મેનેજર (Co-op Bank AGM)", "M.Com, CAIIB (Banking)", "₹ 1,05,000 / માસિક"),
        ("પ્રાયમરી સ્કૂલ શિક્ષક (Primary School Teacher)", "P.T.C., B.A. Primary Education, TET Qualified", "₹ 55,000 / માસિક"),
        ("હોટેલ અને હોસ્પિટાલિટી બિઝનેસ (Hotel & Hospitality Business)", "Bachelor of Hotel Management (BHM)", "₹ 1,90,000 / માસિક"),
        ("લેબોરેટરી પેથોલોજિસ્ટ (Pathology Lab Director)", "M.B.B.S., M.D. (Pathology)", "₹ 2,30,000 / માસિક"),
        ("સાયબર સિક્યોરિટી એનાલિસ્ટ (Cyber Security Analyst)", "B.E. Information Security & CEH Certified", "₹ 1,30,000 / માસિક"),
        ("જ્વેલરી શોરૂમ ઓનર (Jewellery Business Owner)", "B.Com, Graduate Gemologist (GIA)", "₹ 3,50,000 / માસિક"),
        ("એગ્રીકલ્ચર કન્સલ્ટન્ટ (Agricultural Consultant)", "B.Sc. Agriculture, M.Sc. Agronomy", "₹ 90,000 / માસિક"),
        ("પબ્લિક પ્રોસિક્યુટર (Public Prosecutor)", "B.Sc., LL.B. (Special), Bar Council Certified", "₹ 1,15,000 / માસિક"),
        ("પીડિયાટ્રિશિયન / બાળરોગ નિષ્ણાત (Pediatrician Doctor)", "M.B.B.S., D.C.H., M.D. (Pediatrics)", "₹ 2,40,000 / માસિક"),
        ("રિયલ એસ્ટેટ ડેવલપર (Real Estate Developer)", "B.E. Civil, Construction Management", "₹ 4,00,000 / માસિક"),
        ("માર્કેટિંગ મેનેજર - ફાર્મા (Pharma Marketing Manager)", "B.Sc., MBA (Pharmaceutical Marketing)", "₹ 1,35,000 / માસિક"),
        ("મ્યુઝિક ડાયરેક્ટર અને શાસ્ત્રીય ગાયક (Music Director & Vocalist)", "સંગીત વિશારદ, અલંકાર (અખિલ ભારતીય ગાંધર્વ મહાવિદ્યાલય)", "₹ 70,000 / માસિક"),
        ("ક્લાઉડ સોલ્યુશન્સ આર્કિટેક્ટ (Cloud Solutions Architect)", "B.E. Computer, AWS Certified Solutions Architect", "₹ 2,60,000 / માસિક"),
        ("એન્વાયર્નમેન્ટલ એન્જિનિયર (Environmental Engineer)", "B.E. Environmental Engineering (GPCB Consultant)", "₹ 1,00,000 / માસિક"),
        ("ઓપ્ટોમેટ્રિસ્ટ અને આઈ કેર (Optometrist & Eye Clinic)", "Bachelor of Clinical Optometry (B.Optom)", "₹ 85,000 / માસિક"),
        ("સર્ટિફાઇડ ફાયનાન્સિયલ પ્લાનર (Certified Financial Planner - CFP)", "B.Com, Certified Financial Planner (CFP)", "₹ 1,20,000 / માસિક"),
        ("પ્રિન્ટિંગ પ્રેસ માલિક (Printing & Publishing Press Owner)", "Diploma in Printing Technology (DPT)", "₹ 95,000 / માસિક"),
        ("યોગ અને નેચરોપેથી થેરાપિસ્ટ (Yoga & Naturopathy Consultant)", "B.N.Y.S. (Naturopathy & Yogic Sciences)", "₹ 65,000 / માસિક"),
        ("ઈવેન્ટ મેનેજર અને ડેકોરેટર (Event Management Director)", "MBA (Event Management & PR)", "₹ 1,50,000 / માસિક"),
        ("એરોસ્પેસ એન્જિનિયર (Aerospace Engineer)", "B.Tech Aerospace Engineering (ISRO Vendor)", "₹ 1,80,000 / માસિક"),
        ("સુપરિન્ટેન્ડેન્ટ ઓફ સેન્ટ્રલ જીએસટી (Superintendent of Central GST)", "M.Com, Central Excise Inspector Qualified", "₹ 1,25,000 / માસિક"),
        ("કન્સ્ટ્રક્શન પ્રોજેક્ટ એન્જિનિયર (Construction Project Engineer)", "Diploma Civil Engineering, BE Civil", "₹ 1,10,000 / માસિક"),
        ("બાયોટેકનોલોજી રિસર્ચર (Biotechnology Researcher)", "M.Sc. Biotechnology, CSIR-NET Junior Fellow", "₹ 80,000 / માસિક"),
        ("કોમર્સ કોલેજ પ્રિન્સિપાલ (Commerce College Principal)", "M.Com, M.Phil, Ph.D. (Accountancy)", "₹ 1,40,000 / માસિક"),
        ("રેડિયોલોજિસ્ટ તબીબ (Radiologist - DMRD)", "M.B.B.S., DMRD (Radiodiagnosis)", "₹ 2,90,000 / માસિક"),
        ("ટેક્સટાઇલ મિલ જનરલ મેનેજર (Textile Mill General Manager)", "B.Tech Textile Technology", "₹ 1,65,000 / માસિક"),
        ("નેટવર્ક અને સિસ્ટમ્સ એન્જિનિયર (Network & Hardware Engineer)", "B.C.A., CCNA, MCSE Certified", "₹ 70,000 / માસિક"),
        ("ટૂર અને ટ્રાવેલ્સ ઓપરેટર (Tour & Travels Operator)", "Bachelor of Tourism Studies (BTS)", "₹ 1,15,000 / માસિક"),
        ("ચીફ ફિઝિયોથેરાપિસ્ટ (Senior Physiotherapist)", "Bachelor of Physiotherapy (BPT), MPT (Ortho)", "₹ 95,000 / માસિક"),
        ("ક્લિનિકલ ડાયેટિશિયન (Dietitian & Nutritionist)", "M.Sc. Food & Nutrition, Registered Dietitian (RD)", "₹ 75,000 / માસિક"),
        ("કોર્પોરેટ કાનૂની સલાહકાર (Corporate Legal Advisor)", "LL.B., Company Secretary (CS - ICSI)", "₹ 1,90,000 / માસિક"),
        ("વેટરનરી ડોક્ટર / પશુ ચિકિત્સક (Veterinary Doctor)", "B.V.Sc. & A.H. (Veterinary Science & Animal Husbandry)", "₹ 90,000 / માસિક"),
        ("મ્યુનિસિપલ ચીફ ઓફિસર (Municipal Chief Officer)", "M.A. Political Science, GPSC Cleared", "₹ 1,15,000 / માસિક"),
        ("ક્વોલિટી કંટ્રોલ મેનેજર (Quality Assurance Manager)", "B.E. Chemical, Six Sigma Black Belt Certified", "₹ 1,40,000 / માસિક"),
        ("સ્ટેટિસ્ટિકલ ઓફિસર (Government Statistical Officer)", "M.Sc. Statistics (Gold Medalist)", "₹ 85,000 / માસિક"),
        ("સીનિયર ઓડિટ ઓફિસર (Senior Audit Officer - CAG)", "M.Com, ICWA / CMA (Cost Accountant)", "₹ 1,30,000 / માસિક"),
        ("માઇક્રોબાયોલોજી લેબ હેડ (Microbiologist)", "M.Sc. Applied Microbiology, Ph.D.", "₹ 1,05,000 / માસિક"),
        ("હાઈસ્કૂલ સાયન્સ ટીચર (Higher Secondary Science Teacher)", "B.Sc., B.Ed (Chemistry & Biology)", "₹ 60,000 / માસિક"),
        ("ફર્નિચર શોરૂમ પ્રોપ્રાઈટર (Furniture Showroom Proprietor)", "B.Com (Interior Furniture Business)", "₹ 1,20,000 / માસિક"),
        ("પાવર ગ્રીડ ઈલેક્ટ્રિકલ એન્જિનિયર (Power Grid Electrical Engineer)", "B.Tech Electrical & Electronics", "₹ 1,25,000 / માસિક"),
        ("બ્લોક ડેવલપમેન્ટ ઓફિસર (Block Development Officer - BDO)", "Master of Social Work (MSW), GPSC", "₹ 90,000 / માસિક"),
        ("ટેલિકોમ નેટવર્ક એન્જિનિયર (Telecom Network Engineer)", "B.E. Electronics & Communication (EC)", "₹ 1,00,000 / માસિક"),
        ("હોમિયોપેથિક તબીબ (Homeopathic Doctor - BHMS)", "B.H.M.S. (Homeopathic Medicine & Surgery)", "₹ 85,000 / માસિક"),
        ("ન્યુક્લિયર પાવર ટેકનિશિયન (Nuclear Power Plant Engineer)", "M.Sc. Nuclear Physics, NPCIL Fellow", "₹ 1,60,000 / માસિક"),
        ("ડેરી પ્રોડક્ટ્સ ડિસ્ટ્રિબ્યુટર (Dairy Products Distributor)", "B.Sc. Dairy Technology (Anand Agriculture Univ)", "₹ 1,40,000 / માસિક"),
        ("કન્સલ્ટન્ટ કાર્ડિયોલોજિસ્ટ (Consultant Cardiologist)", "M.B.B.S., M.D., D.M. (Cardiology)", "₹ 4,50,000 / માસિક"),
        ("એજ્યુકેશનલ કન્સલ્ટન્ટ (Overseas Education Consultant)", "Master of Education (M.Ed), British Council Certified", "₹ 1,35,000 / માસિક"),
        ("લોજિસ્ટિક્સ અને ટ્રાન્સપોર્ટ મેનેજર (Logistics & Transport Manager)", "MBA (Supply Chain & Logistics Management)", "₹ 1,15,000 / માસિક"),
        ("આયુર્વેદિક ચિકિત્સક / વૈદ્ય (Ayurvedic Doctor - BAMS)", "B.A.M.S. (Ayurvedacharya, Gujarat Ayurved Univ)", "₹ 95,000 / માસિક"),
        ("રિસર્ચ સ્કોલર (Academic Research Scholar)", "Ph.D. in Theoretical Physics, DST INSPIRE Fellow", "₹ 65,000 / માસિક"),
        ("સિરામિક ટાઇલ્સ ટ્રેડર (Ceramic & Sanitaryware Trader)", "B.Com, Ceramic Technology Diploma", "₹ 2,00,000 / માસિક"),
        ("સ્પોર્ટ્સ કોચ / ફિટનેસ ટ્રેનર (Sports Coach & Physical Educator)", "B.P.Ed, M.P.Ed (Physical Education, Sports Univ)", "₹ 60,000 / માસિક"),
        ("ડ્રગ ઇન્સ્પેક્ટર (Government Drug Inspector)", "B.Pharm, Drug Regulatory Affairs (FDA Gujarat)", "₹ 1,10,000 / માસિક"),
        ("ફુલ સ્ટેક વેબ ડેવલપર (Full Stack Web Developer)", "B.Tech Computer Science, React/Node Certified", "₹ 1,45,000 / માસિક"),
        ("ઇલેક્ટ્રોનિક્સ શોરૂમ માલિક (Consumer Electronics Retailer)", "B.E. Instrumentation & Control", "₹ 1,80,000 / માસિક"),
        ("જનરલ સર્જન તબીબ (MS General Surgeon)", "M.B.B.S., M.S. (General Surgery), FIAGES", "₹ 3,00,000 / માસિક"),
        ("સોઇલ સાયન્ટિસ્ટ (Soil & Agricultural Scientist)", "M.Sc. Soil Science & Agricultural Chemistry", "₹ 85,000 / માસિક"),
        ("ઔદ્યોગિક સેફ્ટી ઓફિસર (Industrial Safety Officer)", "B.Sc. Fire & Industrial Safety Engineering (DISHA)", "₹ 95,000 / માસિક"),
        ("ગુજરાતી સાહિત્ય તંત્રી (Gujarati Literature Editor)", "M.A. Gujarati Literature, Sahitya Parishad Fellow", "₹ 60,000 / માસિક"),
        ("સોલાર એનર્જી કન્સલ્ટન્ટ (Solar Energy Solutions Consultant)", "B.E. Renewable Energy Systems, MNRE Certified", "₹ 1,25,000 / માસિક"),
        ("કેમિકલ પ્લાન્ટ સુપરવાઇઝર (Chemical Plant Production Supervisor)", "Diploma in Chemical Engineering", "₹ 75,000 / માસિક"),
        ("એગ્રો કેમિકલ્સ વેપારી (Agrochemicals Merchant)", "B.Sc. Botany, M.Sc. Horticulture", "₹ 1,60,000 / માસિક"),
        ("ચીફ મરીન એન્જિનિયર (Chief Marine Engineer)", "B.E. Marine Engineering (Class-1 MOT Certified)", "₹ 3,80,000 / માસિક"),
        ("હોસ્પિટલ એડમિનિસ્ટ્રેટર (Hospital Administrator - MHA)", "Master of Hospital Administration (MHA, TISS)", "₹ 1,50,000 / માસિક"),
        ("સિવિલ જજ અને મેજિસ્ટ્રેટ (Civil Judge & Judicial Magistrate)", "LL.B., LL.M. (Constitutional Law), GPSC Judicial", "₹ 1,75,000 / માસિક"),
        ("વેધર ફોરકાસ્ટર અને મીટીઅરોલોજિસ્ટ (Meteorologist)", "M.Sc. Meteorology & Atmospheric Sciences", "₹ 1,05,000 / માસિક"),
        ("વાસ્તુ અને ઇન્ટિરિયર નિષ્ણાત (Vastu & Interior Decorator)", "B.A., Vastu Shastra Acharya Diploma", "₹ 80,000 / માસિક"),
        ("ફૂડ સેફ્ટી ઓફિસર (Government Food Safety Officer)", "B.Tech Food Processing Technology, FSSAI Certified", "₹ 90,000 / માસિક"),
        ("૩ડી એનિમેશન અને VFX આર્ટિસ્ટ (3D Animation & VFX Artist)", "Diploma in 3D Animation & Maya (Arena)", "₹ 70,000 / માસિક"),
        ("ઓટોમોટિવ સર્વિસ સ્ટેશન માલિક (Automotive Service Station Owner)", "Diploma in Automobile Engineering", "₹ 1,30,000 / માસિક"),
        ("આંતરરાષ્ટ્રીય વેપાર નિકાસકાર (International Trade & Export Consultant)", "MBA (International Business & Foreign Trade)", "₹ 2,50,000 / માસિક")
    ]

    city_dist_vill = [
        ("અમદાવાદ", "અમદાવાદ", "ઈડર, જિ. સાબરકાંઠા", "380015"),
        ("ગાંધીનગર", "ગાંધીનગર", "પ્રાંતિજ, સાબરકાંઠા", "382010"),
        ("વડોદરા", "વડોદરા", "સિદ્ધપુર, જિ. પાટણ", "390001"),
        ("સુરત", "સુરત", "તલોદ, જિ. સાબરકાંઠા", "395007"),
        ("રાજકોટ", "રાજકોટ", "વડનગર, જિ. મહેસાણા", "360001"),
        ("ભાવનગર", "ભાવનગર", "મોડાસા, અરવલ્લી", "364001"),
        ("જામનગર", "જામનગર", "વિજયનગર, સાબરકાંઠા", "361001"),
        ("જૂનાગઢ", "જૂનાગઢ", "ખેડબ્રહ્મા, સાબરકાંઠા", "362001"),
        ("મહેસાણા", "મહેસાણા", "ભિલોડા, અરવલ્લી", "384001"),
        ("પાટણ", "પાટણ", "સિદ્ધપુર પાટણ", "384265"),
        ("હિંમતનગર", "સાબરકાંઠા", "ઈડર, સાબરકાંઠા", "383001"),
        ("ઈડર", "સાબરકાંઠા", "ઈડર ગઢ પાસે", "383430"),
        ("પ્રાંતિજ", "સાબરકાંઠા", "પ્રાંતિજ રેલવે સ્ટેશન રોડ", "383205"),
        ("તલોદ", "સાબરકાંઠા", "તલોદ બજાર", "383215"),
        ("મોડાસા", "અરવલ્લી", "મોડાસા ટાઉન", "383315"),
        ("ખેડબ્રહ્મા", "સાબરકાંઠા", "અંબિકા મંદિર રોડ, ખેડબ્રહ્મા", "383255"),
        ("પાલનપુર", "બનાસકાંઠા", "પાલનપુર કિલ્લા રોડ", "385001"),
        ("નડિયાદ", "ખેડા", "સંતરામ મંદિર રોડ, નડિયાદ", "387001"),
        ("આણંદ", "આણંદ", "અમૂલ ડેરી રોડ, આણંદ", "388001"),
        ("ભરૂચ", "ભરૂચ", "ઝાડેશ્વર, ભરૂચ", "392001"),
        ("નવસારી", "નવસારી", "દાંડી રોડ, નવસારી", "396445"),
        ("વલસાડ", "વલસાડ", "તિથલ, વલસાડ", "396001"),
        ("મોરબી", "મોરબી", "દરબારગઢ, મોરબી", "363641"),
        ("પોરબંદર", "પોરબંદર", "સુદામાપુરી, પોરબંદર", "360575")
    ]

    blood_groups_pool = ["A+", "B+", "O+", "AB+", "A-", "B-", "O-", "AB+"]
    samaj_pool = [
        "શ્રી સમસ્ત ગુજરાત બ્રહ્મ સમાજ",
        "ઔદીચ્ય સહસ્ત્ર બ્રહ્મ સમાજ",
        "ખેડાવળ બ્રહ્મ સમાજ",
        "પ્રશ્નોરા નાગર બ્રહ્મ સમાજ",
        "મોઢ બ્રહ્મ સમાજ",
        "સિદ્ધપુરા ઔદીચ્ય બ્રહ્મ સમાજ",
        "ઝાલાવાડી ઔદીચ્ય બ્રહ્મ સમાજ",
        "સાંચોરા બ્રહ્મ સમાજ",
        "રાજગોર બ્રહ્મ સમાજ",
        "બ્રહ્મભટ્ટ સમાજ"
    ]
    fee_pool = ["આજીવન (Life Member)", "₹ 1000", "₹ 500", "આજીવન (Life Member)", "₹ 2000"]

    family_female_names = [
        "ગીતાબેન", "પૂજાબેન", "વર્ષાબેન", "રેખાબેન", "નીતાબેન", "અલ્પાબેન", "ભાવનાબેન",
        "દર્શનાબેન", "હંસાબેન", "કલ્પનાબેન", "મીનાબેન", "નયનાબેન", "પ્રતિમાબેન", "રૂપલબેન",
        "સંગીતાબેન", "તૃપ્તિબેન", "વંદનાબેન", "જાગૃતિબેન", "ચેતનાબેન", "દીપ્તિબેન",
        "ફાલ્ગુનીબેન", "હેમાબેન", "ઇલાબેન", "જ્યોતિબેન", "કોકિલાબેન", "માયાબેન", "નમ્રતાબેન"
    ]

    family_child_m = [
        "આરવ", "ધ્રુવ", "આદિત્ય", "રોહન", "મિહીર", "કેવલ", "હર્ષિલ", "વેદાંત", "પ્રિતેશ",
        "દેવ", "આરુષ", "વિહાન", "કબીર", "ઓમ", "શૌર્ય", "અર્જુન", "તક્ષ", "શિવ", "આયુષ",
        "દર્શન", "પ્રણવ", "શુભમ", "કુણાલ", "નિસર્ગ", "મોક્ષ", "અક્ષત", "માનવ", "હર્ષ"
    ]

    family_child_f = [
        "અનન્યા", "કિયા", "યશવી", "અન્વી", "કુંજલ", "માનસી", "અવની", "દિયા", "ઈશા",
        "આરાધ્યા", "પરી", "રિયા", "સાંચી", "માહી", "ખુશી", "દિશા", "સિયા", "તન્વી",
        "પ્રિશા", "ધ્વનિ", "કાવ્યા", "અદિતિ", "વૈદેહી", "શ્રુતિ", "સ્મૃતિ", "નિરાલી"
    ]

    # Generate records 21 to 100 (80 records)
    for idx in range(21, 101):
        i = idx - 21
        # alternate gender of primary member (85% male, 15% female head)
        is_female_head = (idx % 7 == 0)
        surname = surnames[i % len(surnames)]
        father = father_names[i % len(father_names)]
        if is_female_head:
            fname = first_names_f[(i // 2) % len(first_names_f)]
            full_name = f"{surname} {fname} {father}"
        else:
            fname = first_names_m[i % len(first_names_m)]
            full_name = f"{surname} {fname} {father}"

        occ_info = occupations_data[i % len(occupations_data)]
        loc_info = city_dist_vill[i % len(city_dist_vill)]

        mob_str = f"982501{idx:04d}"
        landline_str = f"0{loc_info[3][:3]}-2{idx:05d}" if idx % 3 == 0 else ""
        eng_fname = f"user{idx}"
        email_str = f"brahm.member{idx}@{['gmail.com', 'yahoo.com', 'outlook.com'][idx % 3]}"

        birth_year = 1965 + (idx % 35)
        birth_month = 1 + (idx % 12)
        birth_day = 1 + (idx % 28)
        bdate = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"

        # Family members generation (2 to 4 members per member)
        fam_list = []
        spouse_name = family_female_names[(i * 3 + 1) % len(family_female_names)]
        child1_m = family_child_m[(i * 2) % len(family_child_m)]
        child2_f = family_child_f[(i * 2 + 1) % len(family_child_f)]

        if not is_female_head:
            fam_list.append({
                "name": f"{spouse_name} {fname} {surname}",
                "relation": "પત્ની (Wife)",
                "age": max(22, 2026 - birth_year - 3),
                "education": ["B.A.", "B.Com", "M.A.", "B.Sc.", "M.Com", "B.Ed"][idx % 6],
                "occupation": ["ગૃહિણી (Housewife)", "શિક્ષિકા (Teacher)", "બેંક આસિસ્ટન્ટ", "ગૃહિણી અને ટ્યુશન"][idx % 4],
                "blood_group": blood_groups_pool[(idx + 1) % len(blood_groups_pool)],
                "contact": f"982502{idx:04d}"
            })
            fam_list.append({
                "name": f"{child1_m} {fname} {surname}",
                "relation": "પુત્ર (Son)",
                "age": max(5, min(26, (2026 - birth_year - 24))),
                "education": ["ધોરણ ૮", "ધોરણ ૧૦", "ધોરણ ૧૨ સાયન્સ", "B.Tech IT", "B.Com", "B.E. Mechanical"][idx % 6],
                "occupation": ["વિદ્યાર્થી (Student)", "વિદ્યાર્થી (Student)", "સોફ્ટવેર ડેવલપર", "જુનિયર એન્જિનિયર"][idx % 4],
                "blood_group": blood_groups_pool[(idx + 2) % len(blood_groups_pool)],
                "contact": f"982503{idx:04d}" if (2026 - birth_year - 24) >= 18 else ""
            })
            if idx % 2 == 0:
                fam_list.append({
                    "name": f"{child2_f} {fname} {surname}",
                    "relation": "પુત્રી (Daughter)",
                    "age": max(3, min(22, (2026 - birth_year - 27))),
                    "education": ["ધોરણ ૫", "ધોરણ ૯", "ધોરણ ૧૨ આર્ટ્સ", "B.B.A.", "B.Sc. Nursing"][idx % 5],
                    "occupation": ["વિદ્યાર્થી (Student)", "વિદ્યાર્થી (Student)", "વિદ્યાર્થી (College Student)", "નર્સિંગ સ્ટાફ"][idx % 4],
                    "blood_group": blood_groups_pool[(idx + 3) % len(blood_groups_pool)],
                    "contact": ""
                })
            if idx % 5 == 0:
                fam_list.append({
                    "name": f"{father} {surname}",
                    "relation": "પિતા (Father)",
                    "age": min(88, 2026 - birth_year + 26),
                    "education": "મેટ્રિક (Old SSC)",
                    "occupation": "નિવૃત્ત સરકારી કર્મચારી (Retired)",
                    "blood_group": blood_groups_pool[(idx + 4) % len(blood_groups_pool)],
                    "contact": ""
                })
        else:
            fam_list.append({
                "name": f"{father_names[(i+5) % len(father_names)]} {surname}",
                "relation": "પતિ (Husband)",
                "age": max(25, 2026 - birth_year + 2),
                "education": ["B.Com", "B.E. Civil", "M.A.", "B.Sc."][idx % 4],
                "occupation": ["સ્વતંત્ર વેપાર (Business)", "સિવિલ એન્જિનિયર", "ખાનગી નોકરી"][idx % 3],
                "blood_group": blood_groups_pool[(idx + 1) % len(blood_groups_pool)],
                "contact": f"982502{idx:04d}"
            })
            fam_list.append({
                "name": f"{child1_m} {surname}",
                "relation": "પુત્ર (Son)",
                "age": max(6, min(24, (2026 - birth_year - 24))),
                "education": ["ધોરણ ૭", "ધોરણ ૧૧ સાયન્સ", "B.C.A."][idx % 3],
                "occupation": "વિદ્યાર્થી (Student)",
                "blood_group": blood_groups_pool[(idx + 2) % len(blood_groups_pool)],
                "contact": ""
            })

        members.append({
            "code_num": idx,
            "first_name": fname,
            "father_name": father,
            "surname": surname,
            "mobile": mob_str,
            "landline": landline_str,
            "email": email_str,
            "address": f"{idx * 3}, ગાયત્રી નગર, સ્ટેશન રોડ",
            "village_address": loc_info[2],
            "city": loc_info[0],
            "district": loc_info[1],
            "state": "Gujarat",
            "pincode": loc_info[3],
            "occupation": occ_info[0],
            "business_address": f"{loc_info[0]} સેન્ટ્રલ બજાર, {loc_info[1]}",
            "income": occ_info[2],
            "education": occ_info[1],
            "blood_group": blood_groups_pool[idx % len(blood_groups_pool)],
            "samaj": samaj_pool[idx % len(samaj_pool)],
            "fee": fee_pool[idx % len(fee_pool)],
            "birth_date": bdate,
            "family": fam_list
        })

    return members


def run_seed():
    print("Initializing database...")
    init_db()

    all_members = generate_all_100_members()
    print(f"Total members prepared: {len(all_members)}")

    with get_session() as session:
        # First, check existing count
        existing_count = session.query(Member).count()
        print(f"Current member count in DB: {existing_count}")

        if existing_count > 0:
            print("Purging existing data to ensure pristine sequence 1 to 100...")
            session.query(FamilyMember).delete()
            session.query(Member).delete()
            session.commit()

        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        total_family_added = 0
        for m_data in all_members:
            code = f"GBS-{m_data['code_num']:06d}"
            full_name = f"{m_data['surname']} {m_data['first_name']} {m_data['father_name']}"

            member = Member(
                member_code      = code,
                full_name        = full_name,
                surname          = m_data['surname'],
                father_name      = m_data['father_name'],
                mobile           = m_data['mobile'],
                phone_landline   = m_data['landline'],
                email            = m_data['email'],
                address          = m_data['address'],
                village_address  = m_data['village_address'],
                city             = m_data['city'],
                district         = m_data['district'],
                state            = m_data['state'],
                pincode          = m_data['pincode'],
                occupation       = m_data['occupation'],
                business_address = m_data['business_address'],
                income           = m_data['income'],
                education        = m_data['education'],
                blood_group      = m_data['blood_group'],
                samaj            = m_data['samaj'],
                membership_fee   = m_data['fee'],
                signature_text   = full_name,
                birth_date       = m_data['birth_date'],
                created_at       = now_str,
                updated_at       = now_str,
            )
            session.add(member)
            session.flush() # assign member.id

            for fam in m_data['family']:
                fm = FamilyMember(
                    member_id      = member.id,
                    name           = fam['name'],
                    relation       = fam['relation'],
                    age            = fam['age'],
                    education      = fam['education'],
                    blood_group    = fam['blood_group'],
                    occupation     = fam['occupation'],
                    contact_number = fam.get('contact', ''),
                    created_at     = now_str,
                    updated_at     = now_str,
                )
                session.add(fm)
                total_family_added += 1

        # Update member_code_last in app_settings
        setting = session.query(AppSetting).filter_by(setting_key='member_code_last').first()
        if setting:
            setting.setting_value = "100"
            setting.updated_at = now_str
        else:
            session.add(AppSetting(setting_key='member_code_last', setting_value="100", updated_at=now_str))

        session.commit()
        print(f"Successfully seeded 100 members and {total_family_added} family members!")

    # Verify search across different criteria
    print("\n--- Running Search Verification Tests ---")
    svc = SearchService()

    test_queries = [
        ("Surname (Gujarati)", "રાવલ"),
        ("Surname (English)", "joshi"),
        ("Occupation (Doctor)", "તબીબ"),
        ("Occupation (Teacher/English)", "teacher"),
        ("Occupation (Engineer)", "એન્જિનિયર"),
        ("Occupation (Advocate)", "વકીલ"),
        ("Occupation (CA)", "ચાર્ટર્ડ"),
        ("Study (M.B.B.S.)", "M.B.B.S."),
        ("Study (Computer Engineering)", "Computer Engineering"),
        ("City (Ahmedabad)", "અમદાવાદ"),
        ("City (Himatnagar)", "Himatnagar"),
        ("Member Code (Exact)", "GBS-000042"),
        ("Family Member Name", "અનન્યા"),
        ("Family Member Occupation", "ગૃહિણી"),
    ]

    for label, query in test_queries:
        results = svc.search(query)
        print(f"Query '{query}' [{label}]: {len(results)} matches found")
        if results:
            first = results[0]
            print(f"   -> Top Match: {first.member_code} | {first.full_name} | {first.city} | {first.occupation} | {first.education}")
        else:
            print(f"   -> No match found for '{query}'!")

if __name__ == '__main__':
    run_seed()
