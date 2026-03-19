"""
DOCX text extraction, Groq-based MCQ generation, and Excel parsing for assignments.
"""
import zipfile
from xml.etree import ElementTree as ET
from django.conf import settings


def extract_text_from_docx(docx_file) -> str:
    """Extract text from uploaded DOCX file without extra dependencies."""
    try:
        with zipfile.ZipFile(docx_file) as archive:
            xml_bytes = archive.read('word/document.xml')
    except Exception:
        return ""

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return ""

    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs = []
    for paragraph in root.findall('.//w:p', ns):
        texts = [node.text for node in paragraph.findall('.//w:t', ns) if node.text]
        if texts:
            paragraphs.append(''.join(texts))
    return "\n\n".join(paragraphs)[:12000]


def generate_mcqs_from_text_groq(text: str, num_questions: int = 20) -> tuple[list, str | None]:
    """
    Use Groq API to generate num_questions MCQs with difficulty (easy/medium/hard).
    Returns list of dicts: {question_text, opt1, opt2, opt3, opt4, correct_answer (1-4), difficulty}.
    """
    api_key = getattr(settings, 'GROQ_API_KEY', None)
    if not api_key:
        return [], "GROQ_API_KEY is not configured."
    if not text.strip():
        return [], "No readable text was found in the selected file."

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        model = getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant')
    except ModuleNotFoundError:
        return [], "The 'groq' Python package is not installed."
    except Exception as exc:
        return [], f"Failed to initialize Groq client: {exc}"

    prompt = f"""Based on the following content, generate exactly {num_questions} multiple choice questions.
Mix difficulties: about 7 easy, 7 medium, 6 hard.

Content:
{text[:10000]}

Match this exact spreadsheet-style schema for every generated question:
Question | Option1 | Option2 | Option3 | Option4 | Answer | Difficulty

For each question output a single line in this exact machine-readable format (no other text):
QUESTION|||option1|||option2|||option3|||option4|||correct_index|||difficulty
- correct_index is 1, 2, 3, or 4 (which option is correct).
- difficulty is one of: easy, medium, hard.
- Replace QUESTION with the question text. Use ||| as separator only between fields.
Output exactly {num_questions} lines, one per question."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0.3,
        )
        raw = (response.choices[0].message.content or "").strip()
    except Exception as exc:
        return [], f"Groq request failed: {exc}"

    questions = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line or "|||" not in line:
            continue
        parts = line.split("|||", 6)
        if len(parts) < 7:
            continue
        q_text = parts[0].strip()
        opt1, opt2, opt3, opt4 = parts[1].strip(), parts[2].strip(), parts[3].strip(), parts[4].strip()
        try:
            correct = int(parts[5].strip())
            if correct not in (1, 2, 3, 4):
                correct = 1
        except (ValueError, IndexError):
            correct = 1
        diff = (parts[6].strip() or "medium").lower()
        if diff not in ("easy", "medium", "hard"):
            diff = "medium"
        if q_text and opt1 and opt2:
            questions.append({
                "question_text": q_text[:2000],
                "opt1": opt1[:500], "opt2": opt2[:500], "opt3": opt3[:500], "opt4": opt4[:500],
                "correct_answer": correct,
                "difficulty": diff,
            })
    if not questions:
        return [], "Groq returned no parsable questions."
    return questions[:num_questions], None


def parse_excel_questions(excel_file) -> list:
    """
    Parse Excel with columns like:
    Question, Option1, Option2, Option3, Option4, Answer, Difficulty
    Also accepts qn/opt1/... aliases.
    Answer can be 1-4, A-D, or the exact option text.
    """
    try:
        import openpyxl
        wb = openpyxl.load_workbook(excel_file, read_only=True, data_only=True)
        ws = wb.active
    except Exception:
        return []

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []

    header = [str(c).strip().lower().replace(" ", "") if c else "" for c in rows[0]]
    def col(name, aliases):
        for a in aliases:
            for i, h in enumerate(header):
                if a in h or h == a:
                    return i
        return None
    i_qn = col("qn", ["qn", "question", "question_text"])
    i_opt1 = col("opt1", ["opt1", "option1"])
    i_opt2 = col("opt2", ["opt2", "option2"])
    i_opt3 = col("opt3", ["opt3", "option3"])
    i_opt4 = col("opt4", ["opt4", "option4"])
    i_ans = col("answer", ["answer", "correct", "correct_answer"])
    i_diff = col("difficulty", ["difficulty", "level", "weightlevel"])
    if i_qn is None or i_opt1 is None or i_opt2 is None:
        return []

    questions = []
    for row in rows[1:]:
        if not row or len(row) <= max(i_qn, i_opt1, i_opt2):
            continue
        qn = row[i_qn]
        if qn is None or (isinstance(qn, str) and not qn.strip()):
            continue
        opt1 = str(row[i_opt1] or "").strip()[:500]
        opt2 = str(row[i_opt2] or "").strip()[:500]
        opt3 = str(row[i_opt3] or "").strip()[:500] if i_opt3 is not None else ""
        opt4 = str(row[i_opt4] or "").strip()[:500] if i_opt4 is not None else ""
        ans = row[i_ans] if i_ans is not None and i_ans < len(row) else 1
        if isinstance(ans, str):
            ans_norm = str(ans).strip()
            upper = ans_norm.upper()
            if upper in {"1", "2", "3", "4"}:
                correct = int(upper)
            elif upper in {"A", "B", "C", "D"}:
                correct = {"A": 1, "B": 2, "C": 3, "D": 4}[upper]
            else:
                options = [opt1, opt2, opt3, opt4]
                normalized_options = [opt.strip().lower() for opt in options]
                try:
                    correct = normalized_options.index(ans_norm.lower()) + 1
                except ValueError:
                    correct = 1
        else:
            try:
                correct = int(ans) if ans else 1
                correct = min(max(correct, 1), 4)
            except (TypeError, ValueError):
                correct = 1
        diff_value = str(row[i_diff] or "").strip().lower() if i_diff is not None and i_diff < len(row) else "medium"
        if diff_value not in {"easy", "medium", "hard"}:
            diff_value = "medium"
        if not opt1 or not opt2:
            continue
        questions.append({
            "question_text": str(qn)[:2000],
            "opt1": opt1, "opt2": opt2, "opt3": opt3, "opt4": opt4,
            "correct_answer": correct,
            "difficulty": diff_value,
        })
    return questions
