# app/ingestion/metadata.py
def detect_language(text):

    text_lower = text.lower()

    # =========================
    # C++
    # =========================
    cpp_patterns = [
        "#include",
        "cout <<",
        "cin >>",
        "using namespace std",
        "int main(",
        "std::"
    ]

    # =========================
    # Python
    # =========================
    py_patterns = [
        "def ",
        "print(",
        "if __name__",
        "import ",
        "class "
    ]

    if any(p in text for p in cpp_patterns):
        return "cpp"

    if any(p in text for p in py_patterns):
        return "python"

    return "text"


def detect_topic(text):

    text = text.lower()

    if "recursion" in text:
        return "recursion"

    if "pointer" in text:
        return "pointer"

    if "array" in text:
        return "array"

    if "linked list" in text:
        return "linked_list"

    return "general"