import math
import random
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Dict, List, Optional, Tuple


OFFICIAL_PATTERN = {
    "exam_name": "TS EAPCET Engineering Mock Practice Module",
    "stream": "Engineering",
    "mode": "Computer Based Test (CBT)",
    "duration_minutes": 180,
    "total_questions": 160,
    "total_marks": 160,
    "marking_scheme": {
        "correct_answer": 1,
        "negative_marking": 0
    },
    "sections": [
        {"subject": "Mathematics", "questions": 80},
        {"subject": "Physics", "questions": 40},
        {"subject": "Chemistry", "questions": 40}
    ],
    "languages": ["English", "Telugu", "Urdu"],
    "official_sources": [
        {
            "title": "TS EAPCET official portal",
            "url": "https://eapcet.tgche.ac.in/",
            "note": "Use the official portal to verify the latest information bulletin, timetable, answer keys, and master question papers."
        }
    ],
    "instructions": [
        "The paper follows the TS EAPCET engineering pattern: 160 objective questions in 180 minutes.",
        "Each correct answer carries 1 mark and there is no negative marking.",
        "Use the question palette to jump between questions, save answers, or mark items for review.",
        "Answer one option per question; unanswered questions remain unattempted.",
        "This practice module mirrors the official structure and instructions, but every question in the mock set is original practice content."
    ],
    "paper_model_note": "Mock papers follow the official subject breakup and CBT workflow. Question wording is original practice material inspired by recurring concepts from prior paper cycles."
}


PAST_PAPER_CYCLES = [
    {
        "paper_id": 1,
        "title": "Mock Paper 1",
        "inspired_by_year": 2015,
        "focus": {
            "Mathematics": ["Algebra", "Calculus", "Coordinate Geometry"],
            "Physics": ["Mechanics", "Current Electricity", "Optics"],
            "Chemistry": ["Atomic Structure", "Chemical Bonding", "Organic Basics"]
        }
    },
    {
        "paper_id": 2,
        "title": "Mock Paper 2",
        "inspired_by_year": 2016,
        "focus": {
            "Mathematics": ["Probability", "Vectors", "Straight Lines"],
            "Physics": ["Kinematics", "Thermodynamics", "Magnetism"],
            "Chemistry": ["Periodic Trends", "Equilibrium", "Solutions"]
        }
    },
    {
        "paper_id": 3,
        "title": "Mock Paper 3",
        "inspired_by_year": 2017,
        "focus": {
            "Mathematics": ["Binomial Theorem", "Matrices", "Trigonometry"],
            "Physics": ["Work Energy Power", "Electrostatics", "Modern Basics"],
            "Chemistry": ["Redox", "Thermochemistry", "Hydrocarbons"]
        }
    },
    {
        "paper_id": 4,
        "title": "Mock Paper 4",
        "inspired_by_year": 2018,
        "focus": {
            "Mathematics": ["Progressions", "Complex Numbers", "Parabola"],
            "Physics": ["Newtonian Mechanics", "Gravitation", "Ray Optics"],
            "Chemistry": ["Molarity", "VSEPR", "Polymers"]
        }
    },
    {
        "paper_id": 5,
        "title": "Mock Paper 5",
        "inspired_by_year": 2019,
        "focus": {
            "Mathematics": ["Limits", "Differentiation", "Permutation & Combination"],
            "Physics": ["SHM", "Heat", "Electric Force"],
            "Chemistry": ["Atomic Orbitals", "Le Chatelier Principle", "Biomolecules"]
        }
    },
    {
        "paper_id": 6,
        "title": "Mock Paper 6",
        "inspired_by_year": 2020,
        "focus": {
            "Mathematics": ["Integration", "Probability", "Circles"],
            "Physics": ["Kinematics", "Current Electricity", "Magnetic Force"],
            "Chemistry": ["Thermodynamics", "Organic Functional Groups", "Periodic Trends"]
        }
    },
    {
        "paper_id": 7,
        "title": "Mock Paper 7",
        "inspired_by_year": 2021,
        "focus": {
            "Mathematics": ["Vectors", "Quadratic Equations", "Matrices"],
            "Physics": ["Mechanics", "Optics", "Electrostatics"],
            "Chemistry": ["Bonding", "Redox", "Hydrocarbons"]
        }
    },
    {
        "paper_id": 8,
        "title": "Mock Paper 8",
        "inspired_by_year": 2022,
        "focus": {
            "Mathematics": ["Trigonometry", "Parabola", "Coordinate Geometry"],
            "Physics": ["Thermodynamics", "Magnetism", "Ray Optics"],
            "Chemistry": ["Solutions", "Equilibrium", "Polymers"]
        }
    },
    {
        "paper_id": 9,
        "title": "Mock Paper 9",
        "inspired_by_year": 2023,
        "focus": {
            "Mathematics": ["Calculus", "Complex Numbers", "Straight Lines"],
            "Physics": ["Work Energy Power", "Gravitation", "Current Electricity"],
            "Chemistry": ["Atomic Structure", "Organic Basics", "Biomolecules"]
        }
    },
    {
        "paper_id": 10,
        "title": "Mock Paper 10",
        "inspired_by_year": 2024,
        "focus": {
            "Mathematics": ["Algebra", "Integration", "Probability"],
            "Physics": ["Mechanics", "Electricity", "Optics"],
            "Chemistry": ["Bonding", "Molarity", "Redox"]
        }
    }
]


def _text(value) -> str:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)
    if isinstance(value, float):
        if math.isclose(value, round(value), rel_tol=1e-9, abs_tol=1e-9):
            return str(int(round(value)))
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def _difficulty(index: int) -> str:
    levels = ["easy", "medium", "hard"]
    return levels[index % len(levels)]


def _make_rng(*parts) -> random.Random:
    return random.Random("|".join(str(part) for part in parts))


def _shuffle_choices(rng: random.Random, correct, distractors: List) -> Tuple[List[str], int]:
    correct_text = _text(correct)
    choices = []
    filler_offset = 1

    for choice in [correct] + distractors:
        text = _text(choice)
        if text not in choices:
            choices.append(text)

    while len(choices) < 4:
        if isinstance(correct, (int, float)):
            filler = _text(float(correct) + filler_offset)
        else:
            filler = f"Option {filler_offset}"
        if filler not in choices:
            choices.append(filler)
        filler_offset += 1

    rng.shuffle(choices)
    return choices[:4], choices.index(correct_text)


@dataclass(frozen=True)
class PracticeQuestion:
    id: str
    question_number: int
    subject: str
    topic: str
    difficulty: str
    prompt: str
    options: List[str]
    correct_option: int
    explanation: str
    inspired_by_year: int

    def to_public_dict(self) -> Dict:
        return {
            "id": self.id,
            "questionNumber": self.question_number,
            "subject": self.subject,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "prompt": self.prompt,
            "options": self.options
        }

    def to_solution_dict(self, selected_option: Optional[int] = None) -> Dict:
        return {
            "id": self.id,
            "questionNumber": self.question_number,
            "subject": self.subject,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "prompt": self.prompt,
            "options": self.options,
            "selectedOption": selected_option,
            "selectedOptionText": self.options[selected_option] if selected_option is not None and 0 <= selected_option < len(self.options) else None,
            "correctOption": self.correct_option,
            "correctOptionText": self.options[self.correct_option],
            "isCorrect": selected_option == self.correct_option if selected_option is not None else False,
            "explanation": self.explanation,
            "inspiredByYear": self.inspired_by_year
        }


def _question(
    paper_id: int,
    question_number: int,
    subject: str,
    topic: str,
    difficulty: str,
    prompt: str,
    options: List[str],
    correct_option: int,
    explanation: str,
    inspired_by_year: int
) -> PracticeQuestion:
    return PracticeQuestion(
        id=f"P{paper_id}-{question_number}",
        question_number=question_number,
        subject=subject,
        topic=topic,
        difficulty=difficulty,
        prompt=prompt,
        options=options,
        correct_option=correct_option,
        explanation=explanation,
        inspired_by_year=inspired_by_year
    )


def _progression_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("progression", paper_id, occurrence)
    a = rng.randint(2, 9)
    d = rng.randint(2, 7)
    n = 2 * rng.randint(4, 9)

    if occurrence % 2 == 0:
        correct = a + (n - 1) * d
        options, correct_option = _shuffle_choices(rng, correct, [correct - d, correct + d, a * n])
        prompt = f"In an arithmetic progression with first term {a} and common difference {d}, the {n}th term is"
        explanation = f"The nth term of an AP is a + (n - 1)d = {a} + ({n} - 1) x {d} = {correct}."
    else:
        correct = n * (2 * a + (n - 1) * d) // 2
        options, correct_option = _shuffle_choices(rng, correct, [correct - n, correct + d, a + d])
        prompt = f"The sum of the first {n} terms of an arithmetic progression with first term {a} and common difference {d} is"
        explanation = f"S_n = n/2 [2a + (n - 1)d] = {n}/2 [2 x {a} + ({n} - 1) x {d}] = {correct}."

    return _question(paper_id, question_number, "Mathematics", "Progressions", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _quadratic_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("quadratic", paper_id, occurrence)
    r1 = rng.randint(1, 6)
    r2 = rng.randint(2, 8)
    s = r1 + r2
    p = r1 * r2

    if occurrence % 2 == 0:
        correct = s
        options, correct_option = _shuffle_choices(rng, correct, [p, s + 1, abs(r1 - r2)])
        prompt = f"If alpha and beta are roots of x^2 - {s}x + {p} = 0, then alpha + beta equals"
        explanation = f"For x^2 - ({s})x + {p} = 0, the sum of roots is {-(-s)} = {s}."
    else:
        correct = p
        options, correct_option = _shuffle_choices(rng, correct, [s, p + s, p - 1 if p > 1 else p + 2])
        prompt = f"If alpha and beta are roots of x^2 - {s}x + {p} = 0, then alpha beta equals"
        explanation = f"For x^2 - ({s})x + {p} = 0, the product of roots is the constant term {p}."

    return _question(paper_id, question_number, "Mathematics", "Quadratic Equations", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _binomial_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("binomial", paper_id, occurrence)
    n = rng.randint(5, 10)
    k = rng.randint(1, n - 1)
    correct = math.comb(n, k)
    options, correct_option = _shuffle_choices(rng, correct, [math.comb(n, k - 1), math.comb(n, min(k + 1, n)), n * k])
    prompt = f"The coefficient of x^{k} in the expansion of (1 + x)^{n} is"
    explanation = f"In (1 + x)^{n}, the coefficient of x^{k} is nCk = {n}C{k} = {correct}."
    return _question(paper_id, question_number, "Mathematics", "Binomial Theorem", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _trigonometry_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("trigonometry", paper_id, occurrence)
    cases = [
        ("sin 30 deg cos 60 deg + cos 30 deg sin 60 deg", "1", ["0", "1/2", "sqrt(3)/2"], "Use sin(A + B). Here A + B = 90 deg, so the value is sin 90 deg = 1."),
        ("sin 45 deg cos 45 deg + cos 45 deg sin 45 deg", "1", ["1/2", "sqrt(3)/2", "0"], "Use sin(A + B). Here A + B = 90 deg, so the value is 1."),
        ("sec^2 theta - tan^2 theta", "1", ["0", "tan theta", "sec theta"], "By the identity sec^2 theta - tan^2 theta = 1."),
        ("sin^2 theta + cos^2 theta", "1", ["0", "2", "sin theta"], "By the basic trigonometric identity, sin^2 theta + cos^2 theta = 1.")
    ]
    prompt_text, correct, distractors, explanation = cases[occurrence % len(cases)]
    options = [correct] + distractors
    rng.shuffle(options)
    return _question(
        paper_id,
        question_number,
        "Mathematics",
        "Trigonometry",
        _difficulty(occurrence),
        f"The value of {prompt_text} is",
        options,
        options.index(correct),
        explanation,
        year
    )


def _coordinate_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("coordinate", paper_id, occurrence)
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    dx, dy, dist = triples[occurrence % len(triples)]
    x1 = rng.randint(-5, 4)
    y1 = rng.randint(-5, 4)
    x2 = x1 + dx
    y2 = y1 + dy
    options, correct_option = _shuffle_choices(rng, dist, [dx + dy, dist - 1, dist + 2])
    prompt = f"The distance between the points ({x1}, {y1}) and ({x2}, {y2}) is"
    explanation = f"Distance = sqrt(({x2} - {x1})^2 + ({y2} - {y1})^2) = sqrt({dx}^2 + {dy}^2) = {dist}."
    return _question(paper_id, question_number, "Mathematics", "Coordinate Geometry", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _circle_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("circle", paper_id, occurrence)
    h = rng.randint(1, 5)
    k = rng.randint(1, 5)
    r = rng.randint(2, 6)
    g = -h
    f = -k
    c = h * h + k * k - r * r
    correct = f"({h}, {k})"
    distractors = [f"({-h}, {k})", f"({h}, {-k})", f"({r}, {r})"]
    options = [correct] + distractors
    rng.shuffle(options)
    prompt = f"The centre of the circle x^2 + y^2 {2 * g:+d}x {2 * f:+d}y {c:+d} = 0 is"
    explanation = f"Compare with x^2 + y^2 + 2gx + 2fy + c = 0. Here g = {g} and f = {f}, so the centre is (-g, -f) = ({h}, {k})."
    return _question(paper_id, question_number, "Mathematics", "Circles", _difficulty(occurrence), prompt, options, options.index(correct), explanation, year)


def _straight_line_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("straight-line", paper_id, occurrence)
    x1 = rng.randint(1, 5)
    y1 = rng.randint(1, 5)
    dx, dy = [(2, 1), (3, 2), (4, 3), (5, 4)][occurrence % 4]
    x2 = x1 + dx
    y2 = y1 + dy
    correct = Fraction(dy, dx)
    distractors = [Fraction(dx, dy), Fraction(dy + 1, dx), Fraction(dy, dx + 1)]
    options, correct_option = _shuffle_choices(rng, correct, distractors)
    prompt = f"The slope of the line passing through ({x1}, {y1}) and ({x2}, {y2}) is"
    explanation = f"Slope = (y2 - y1)/(x2 - x1) = ({y2} - {y1})/({x2} - {x1}) = {dy}/{dx}."
    return _question(paper_id, question_number, "Mathematics", "Straight Lines", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _matrix_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("matrix", paper_id, occurrence)
    a = rng.randint(1, 5)
    b = rng.randint(1, 5)
    c = rng.randint(1, 5)
    d = rng.randint(1, 5)
    correct = a * d - b * c
    options, correct_option = _shuffle_choices(rng, correct, [a * d + b * c, a + d, b + c])
    prompt = f"The determinant of the matrix [[{a}, {b}], [{c}, {d}]] is"
    explanation = f"For a 2 x 2 matrix [[a, b], [c, d]], determinant = ad - bc = {a} x {d} - {b} x {c} = {correct}."
    return _question(paper_id, question_number, "Mathematics", "Matrices", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _probability_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("probability", paper_id, occurrence)
    red = rng.randint(2, 6)
    blue = rng.randint(2, 6)
    green = rng.randint(1, 4)
    total = red + blue + green
    if occurrence % 2 == 0:
        correct = Fraction(red, total)
        prompt = f"A bag contains {red} red, {blue} blue and {green} green balls. The probability of drawing a red ball is"
        explanation = f"Probability = favourable outcomes / total outcomes = {red}/{total}."
    else:
        correct = Fraction(blue + green, total)
        prompt = f"A bag contains {red} red, {blue} blue and {green} green balls. The probability of not drawing a red ball is"
        explanation = f"Not red means blue or green, so probability = ({blue} + {green})/{total} = {blue + green}/{total}."
    distractors = [Fraction(blue, total), Fraction(green, total), Fraction(red + blue, total)]
    options, correct_option = _shuffle_choices(rng, correct, distractors)
    return _question(paper_id, question_number, "Mathematics", "Probability", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _permutation_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("permutation", paper_id, occurrence)
    n = rng.randint(5, 8)
    r = rng.randint(2, 4)
    correct = math.perm(n, r)
    options, correct_option = _shuffle_choices(rng, correct, [math.comb(n, r), n ** r, correct - n])
    prompt = f"The number of ways of arranging {r} objects selected from {n} distinct objects is"
    explanation = f"Required number = nPr = n!/(n-r)! = {n}P{r} = {correct}."
    return _question(paper_id, question_number, "Mathematics", "Permutation and Combination", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _limit_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("limit", paper_id, occurrence)
    a = rng.randint(2, 9)
    if occurrence % 2 == 0:
        correct = 2 * a
        options, correct_option = _shuffle_choices(rng, correct, [a, a * a, 2 * a + 1])
        prompt = f"The value of lim_(x->{a}) (x^2 - {a * a})/(x - {a}) is"
        explanation = f"Factor the numerator: (x - {a})(x + {a}). After cancellation the limit is x + {a}, which becomes {2 * a}."
    else:
        correct = 3 * a * a
        options, correct_option = _shuffle_choices(rng, correct, [a * a, 3 * a, correct + 1])
        prompt = f"The value of lim_(x->{a}) (x^3 - {a ** 3})/(x - {a}) is"
        explanation = f"Factor x^3 - a^3 = (x - a)(x^2 + ax + a^2). Substituting x = {a} gives 3a^2 = {correct}."
    return _question(paper_id, question_number, "Mathematics", "Limits", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _derivative_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("derivative", paper_id, occurrence)
    a = rng.randint(1, 4)
    b = rng.randint(2, 7)
    x0 = rng.randint(1, 4)
    correct = 2 * a * x0 + b
    options, correct_option = _shuffle_choices(rng, correct, [a * x0 * x0 + b * x0, 2 * a + b, correct - a])
    prompt = f"If f(x) = {a}x^2 + {b}x + 3, then f'({x0}) is"
    explanation = f"f'(x) = {2 * a}x + {b}. Therefore f'({x0}) = {2 * a} x {x0} + {b} = {correct}."
    return _question(paper_id, question_number, "Mathematics", "Differentiation", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _integral_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("integral", paper_id, occurrence)
    a = rng.randint(1, 4)
    b = rng.randint(1, 5)
    lower = rng.randint(0, 2)
    upper = lower + rng.randint(1, 3)
    correct = a * (upper * upper - lower * lower) / 2 + b * (upper - lower)
    options, correct_option = _shuffle_choices(rng, correct, [correct + a, correct - b, a * upper + b * upper])
    prompt = f"The value of integral from {lower} to {upper} of ({a}x + {b}) dx is"
    explanation = f"Integrate to get ({a}/2)x^2 + {b}x. Evaluating between {lower} and {upper} gives {correct}."
    return _question(paper_id, question_number, "Mathematics", "Integration", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _vector_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("vector", paper_id, occurrence)
    a1 = rng.randint(1, 5)
    a2 = rng.randint(1, 5)
    b1 = rng.randint(1, 5)
    b2 = rng.randint(1, 5)
    correct = a1 * b1 + a2 * b2
    options, correct_option = _shuffle_choices(rng, correct, [a1 * b2 + a2 * b1, a1 + a2 + b1 + b2, correct - a1])
    prompt = f"The dot product of the vectors ({a1}, {a2}) and ({b1}, {b2}) is"
    explanation = f"a dot b = ({a1})({b1}) + ({a2})({b2}) = {correct}."
    return _question(paper_id, question_number, "Mathematics", "Vectors", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _complex_number_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("complex", paper_id, occurrence)
    a = rng.randint(1, 6)
    b = rng.randint(1, 6)
    if occurrence % 2 == 0:
        correct = a * a + b * b
        options, correct_option = _shuffle_choices(rng, correct, [a + b, abs(a - b), a * b])
        prompt = f"If z = {a} + {b}i, then z multiplied by its conjugate equals"
        explanation = f"z z-bar = ({a} + {b}i)({a} - {b}i) = {a ** 2} + {b ** 2} = {correct}."
    else:
        correct = math.sqrt(a * a + b * b)
        options, correct_option = _shuffle_choices(rng, correct, [a + b, abs(a - b), a * b])
        prompt = f"The modulus of the complex number {a} + {b}i is"
        explanation = f"|z| = sqrt({a}^2 + {b}^2) = sqrt({a * a + b * b}) = {correct}."
    return _question(paper_id, question_number, "Mathematics", "Complex Numbers", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _parabola_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("parabola", paper_id, occurrence)
    a = rng.randint(1, 6)
    correct = f"({a}, 0)"
    distractors = [f"(0, {a})", f"(-{a}, 0)", f"(0, -{a})"]
    options = [correct] + distractors
    rng.shuffle(options)
    prompt = f"The focus of the parabola y^2 = {4 * a}x is"
    explanation = f"Compare with y^2 = 4ax. Here a = {a}, so the focus is ({a}, 0)."
    return _question(paper_id, question_number, "Mathematics", "Parabola", _difficulty(occurrence), prompt, options, options.index(correct), explanation, year)


def _kinematics_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("kinematics", paper_id, occurrence)
    u = rng.randint(2, 8)
    a = rng.randint(1, 4)
    t = rng.randint(2, 6)
    correct = u * t + 0.5 * a * t * t
    options, correct_option = _shuffle_choices(rng, correct, [u * t, 0.5 * a * t * t, correct + a])
    prompt = f"A body starts with initial velocity {u} m/s and acceleration {a} m/s^2. The distance covered in {t} s is"
    explanation = f"Use s = ut + (1/2)at^2 = {u} x {t} + 1/2 x {a} x {t}^2 = {correct} m."
    return _question(paper_id, question_number, "Physics", "Kinematics", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _newton_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("newton", paper_id, occurrence)
    m = rng.randint(2, 10)
    force = rng.randint(10, 40)
    correct = Fraction(force, m)
    distractors = [force * m, Fraction(m, force), force - m]
    options, correct_option = _shuffle_choices(rng, correct, distractors)
    prompt = f"A force of {force} N acts on a body of mass {m} kg. The acceleration produced is"
    explanation = f"By Newton's second law, a = F/m = {force}/{m} = {_text(correct)} m/s^2."
    return _question(paper_id, question_number, "Physics", "Newton's Laws", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _work_energy_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("work-energy", paper_id, occurrence)
    m = rng.randint(1, 6)
    v = rng.randint(2, 10)
    correct = 0.5 * m * v * v
    options, correct_option = _shuffle_choices(rng, correct, [m * v, m * v * v, correct + v])
    prompt = f"The kinetic energy of a {m} kg body moving with speed {v} m/s is"
    explanation = f"Kinetic energy = (1/2)mv^2 = 1/2 x {m} x {v}^2 = {correct} J."
    return _question(paper_id, question_number, "Physics", "Work, Energy and Power", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _shm_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("shm", paper_id, occurrence)
    cases = [
        ("If the mass attached to a spring becomes four times and k remains unchanged, the time period becomes", "2T", ["T", "4T", "T/2"], "For a spring mass system, T = 2pi sqrt(m/k). If mass becomes 4m, T becomes 2T."),
        ("If the mass attached to a spring becomes one-fourth and k remains unchanged, the time period becomes", "T/2", ["T", "2T", "4T"], "T is proportional to sqrt(m), so reducing mass to one-fourth makes the period T/2."),
        ("If the spring constant becomes four times and mass remains unchanged, the time period becomes", "T/2", ["T", "2T", "4T"], "T is proportional to 1/sqrt(k), so increasing k to 4k reduces the period to T/2."),
        ("If the spring constant becomes one-fourth and mass remains unchanged, the time period becomes", "2T", ["T", "T/2", "4T"], "T is proportional to 1/sqrt(k), so reducing k to k/4 doubles the period.")
    ]
    prompt, correct, distractors, explanation = cases[occurrence % len(cases)]
    options = [correct] + distractors
    rng.shuffle(options)
    return _question(paper_id, question_number, "Physics", "Simple Harmonic Motion", _difficulty(occurrence), prompt, options, options.index(correct), explanation, year)


def _gravitation_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("gravitation", paper_id, occurrence)
    multiple = (occurrence % 3) + 1
    correct = Fraction(1, (multiple + 1) ** 2)
    distractors = [Fraction(1, multiple + 1), Fraction(1, multiple ** 2 if multiple > 1 else 4), Fraction(1, multiple + 2)]
    options, correct_option = _shuffle_choices(rng, correct, distractors)
    prompt = f"If a body is taken to a height equal to {multiple}R above the earth's surface, the acceleration due to gravity becomes"
    explanation = f"At height h, g' = g [R/(R + h)]^2. Here h = {multiple}R, so g' = g/(1 + {multiple})^2 = {_text(correct)} g."
    return _question(paper_id, question_number, "Physics", "Gravitation", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _thermodynamics_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("thermodynamics", paper_id, occurrence)
    t1 = rng.randint(250, 350)
    multiplier = (occurrence % 3) + 2
    correct = t1 * multiplier
    options, correct_option = _shuffle_choices(rng, correct, [t1 + multiplier, t1 * (multiplier - 1), correct + 10])
    prompt = f"At constant pressure, the volume of an ideal gas becomes {multiplier} times. If its initial temperature is {t1} K, the final temperature is"
    explanation = f"At constant pressure, V/T is constant. If volume becomes {multiplier}V, temperature becomes {multiplier}T = {correct} K."
    return _question(paper_id, question_number, "Physics", "Thermodynamics", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _electrostatics_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("electrostatics", paper_id, occurrence)
    q1 = rng.randint(1, 5)
    q2 = rng.randint(1, 5)
    r = rng.randint(1, 5)
    correct = 9 * q1 * q2 / (r * r)
    options, correct_option = _shuffle_choices(rng, correct, [9 * q1 * q2 / r, q1 * q2, correct + 1])
    prompt = f"Using k = 9 x 10^9 SI units, the numerical value of electrostatic force between charges {q1} microC and {q2} microC separated by {r} m is proportional to"
    explanation = f"By Coulomb's law, F is proportional to kq1q2/r^2, so the numerical factor is 9 x {q1} x {q2}/{r}^2 = {correct}."
    return _question(paper_id, question_number, "Physics", "Electrostatics", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _current_electricity_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("current", paper_id, occurrence)
    r1 = rng.randint(2, 8)
    r2 = rng.randint(2, 8)
    if occurrence % 2 == 0:
        correct = r1 + r2
        options, correct_option = _shuffle_choices(rng, correct, [Fraction(r1 * r2, r1 + r2), abs(r1 - r2), r1 * r2])
        prompt = f"The equivalent resistance of {r1} ohm and {r2} ohm connected in series is"
        explanation = f"Resistances in series add directly, so R_eq = {r1} + {r2} = {correct} ohm."
    else:
        correct = Fraction(r1 * r2, r1 + r2)
        options, correct_option = _shuffle_choices(rng, correct, [r1 + r2, abs(r1 - r2), r1 * r2])
        prompt = f"The equivalent resistance of {r1} ohm and {r2} ohm connected in parallel is"
        explanation = f"For parallel combination, R_eq = R1R2/(R1 + R2) = {r1} x {r2}/({r1} + {r2}) = {_text(correct)} ohm."
    return _question(paper_id, question_number, "Physics", "Current Electricity", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _magnetism_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("magnetism", paper_id, occurrence)
    b = rng.randint(1, 5)
    i = rng.randint(1, 5)
    l = rng.randint(1, 5)
    correct = b * i * l
    options, correct_option = _shuffle_choices(rng, correct, [b + i + l, b * i + l, correct + b])
    prompt = f"A current carrying conductor of length {l} m carrying {i} A is kept perpendicular to a magnetic field of {b} T. The magnetic force is"
    explanation = f"F = BIL sin theta. For 90 degrees, sin theta = 1, so F = {b} x {i} x {l} = {correct} N."
    return _question(paper_id, question_number, "Physics", "Magnetism", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _optics_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("optics", paper_id, occurrence)
    f = rng.choice([10, 12, 15])
    u = rng.choice([30, 36, 45])
    correct = Fraction(f * u, u - f)
    distractors = [Fraction(f * u, u + f), u - f, f + u]
    options, correct_option = _shuffle_choices(rng, correct, distractors)
    prompt = f"For a convex lens of focal length {f} cm, an object is placed {u} cm away. The image distance is"
    explanation = f"Using 1/f = 1/v + 1/u in magnitude form, v = fu/(u - f) = {f} x {u}/({u} - {f}) = {_text(correct)} cm."
    return _question(paper_id, question_number, "Physics", "Ray Optics", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _atomic_structure_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("atomic", paper_id, occurrence)
    n = (occurrence % 4) + 2
    correct = 2 * n * n
    options, correct_option = _shuffle_choices(rng, correct, [n * n, 2 * n, 2 * (n + 1) * (n + 1)])
    prompt = f"The maximum number of electrons that can be accommodated in the shell with principal quantum number n = {n} is"
    explanation = f"The maximum capacity of a shell is 2n^2 = 2 x {n}^2 = {correct}."
    return _question(paper_id, question_number, "Chemistry", "Atomic Structure", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _periodic_trends_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("periodic", paper_id, occurrence)
    cases = [
        ("Among Na, Mg, Al and Si, the element with the largest atomic radius is", "Na", ["Mg", "Al", "Si"], "Across a period atomic radius decreases from left to right, so Na is largest."),
        ("Among F, Cl, Br and I, the most electronegative element is", "F", ["Cl", "Br", "I"], "Electronegativity decreases down the group. Fluorine is the highest."),
        ("Among Li, Na, K and Rb, the element with the lowest ionization enthalpy is", "Rb", ["Li", "Na", "K"], "Ionization enthalpy decreases down the group, so Rb is the lowest among these."),
        ("Among N, O, F and Ne, the element with the highest first ionization enthalpy is", "Ne", ["N", "O", "F"], "Neon has a filled shell and the highest first ionization enthalpy in this set.")
    ]
    prompt, correct, distractors, explanation = cases[occurrence % len(cases)]
    options = [correct] + distractors
    rng.shuffle(options)
    return _question(paper_id, question_number, "Chemistry", "Periodic Trends", _difficulty(occurrence), prompt, options, options.index(correct), explanation, year)


def _bonding_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("bonding", paper_id, occurrence)
    cases = [
        ("The shape of BF3 is", "Trigonal planar", ["Linear", "Tetrahedral", "Trigonal pyramidal"], "Boron in BF3 has three bond pairs and no lone pair, giving trigonal planar geometry."),
        ("The shape of NH3 is", "Trigonal pyramidal", ["Linear", "Trigonal planar", "Tetrahedral"], "NH3 has three bond pairs and one lone pair, so the molecular shape is trigonal pyramidal."),
        ("The shape of CH4 is", "Tetrahedral", ["Linear", "Bent", "Trigonal pyramidal"], "CH4 has four bond pairs around carbon and no lone pair, giving tetrahedral geometry."),
        ("The shape of BeCl2 in gaseous state is", "Linear", ["Bent", "Tetrahedral", "Trigonal planar"], "BeCl2 has two bond pairs and no lone pair around Be, so it is linear.")
    ]
    prompt, correct, distractors, explanation = cases[occurrence % len(cases)]
    options = [correct] + distractors
    rng.shuffle(options)
    return _question(paper_id, question_number, "Chemistry", "Chemical Bonding", _difficulty(occurrence), prompt, options, options.index(correct), explanation, year)


def _thermochemistry_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("thermochemistry", paper_id, occurrence)
    mass = rng.randint(2, 8) * 100
    delta_t = rng.randint(2, 6)
    correct = mass * delta_t
    options, correct_option = _shuffle_choices(rng, correct, [mass + delta_t, mass * (delta_t + 1), correct - mass])
    prompt = f"If specific heat is taken as 1 J g^-1 K^-1, the heat required to raise the temperature of {mass} g of water by {delta_t} K is"
    explanation = f"q = ms delta T = {mass} x 1 x {delta_t} = {correct} J."
    return _question(paper_id, question_number, "Chemistry", "Thermochemistry", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _equilibrium_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("equilibrium", paper_id, occurrence)
    cases = [
        ("For N2(g) + 3H2(g) <=> 2NH3(g), increasing pressure shifts equilibrium towards", "Products", ["Reactants", "No shift", "Both directions equally"], "The forward side has fewer gaseous moles, so higher pressure shifts equilibrium towards NH3."),
        ("For an exothermic equilibrium, increasing temperature shifts the equilibrium towards", "Reactants", ["Products", "No shift", "Catalyst side"], "Raising temperature favours the endothermic direction, which is the reverse side."),
        ("For the reaction A + B <=> C, the equilibrium constant expression Kc is", "[C]/([A][B])", ["[A][B]/[C]", "[C]^2/([A][B])", "[C]/([A] + [B])"], "Products appear in the numerator and reactants in the denominator, each raised to their stoichiometric powers."),
        ("A catalyst in a reversible reaction", "does not change the equilibrium position", ["shifts equilibrium to products", "shifts equilibrium to reactants", "changes Kc"], "A catalyst speeds up both forward and reverse reactions equally and does not alter equilibrium position.")
    ]
    prompt, correct, distractors, explanation = cases[occurrence % len(cases)]
    options = [correct] + distractors
    rng.shuffle(options)
    return _question(paper_id, question_number, "Chemistry", "Chemical Equilibrium", _difficulty(occurrence), prompt, options, options.index(correct), explanation, year)


def _redox_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("redox", paper_id, occurrence)
    cases = [
        ("The oxidation number of Mn in KMnO4 is", "+7", ["+2", "+4", "+6"], "Let oxidation number of Mn be x. Then 1 + x + 4(-2) = 0, so x = +7."),
        ("The oxidation number of Cr in K2Cr2O7 is", "+6", ["+3", "+7", "+4"], "Let oxidation number of each Cr be x. Then 2(+1) + 2x + 7(-2) = 0, so x = +6."),
        ("The oxidation number of S in H2SO4 is", "+6", ["+4", "+2", "-2"], "2(+1) + x + 4(-2) = 0 gives x = +6."),
        ("The oxidation number of N in NH3 is", "-3", ["+3", "-1", "+5"], "x + 3(+1) = 0 gives x = -3.")
    ]
    prompt, correct, distractors, explanation = cases[occurrence % len(cases)]
    options = [correct] + distractors
    rng.shuffle(options)
    return _question(paper_id, question_number, "Chemistry", "Redox Reactions", _difficulty(occurrence), prompt, options, options.index(correct), explanation, year)


def _solutions_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("solutions", paper_id, occurrence)
    moles = rng.randint(1, 4)
    volume = rng.choice([1, 2, 4])
    correct = Fraction(moles, volume)
    distractors = [moles * volume, Fraction(volume, moles), moles + volume]
    options, correct_option = _shuffle_choices(rng, correct, distractors)
    prompt = f"A solution contains {moles} mole of solute in {volume} litre of solution. Its molarity is"
    explanation = f"Molarity = moles of solute / volume in litres = {moles}/{volume} = {_text(correct)} M."
    return _question(paper_id, question_number, "Chemistry", "Solutions", _difficulty(occurrence), prompt, options, correct_option, explanation, year)


def _organic_basics_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("organic", paper_id, occurrence)
    cases = [
        ("The IUPAC name of CH3CH2OH is", "Ethanol", ["Methanol", "Ethanal", "Ethanoic acid"], "CH3CH2OH is a two-carbon alcohol, so the IUPAC name is ethanol."),
        ("The functional group present in CH3CHO is", "Aldehyde", ["Ketone", "Alcohol", "Carboxylic acid"], "CH3CHO contains the -CHO group, which is an aldehyde."),
        ("The IUPAC name of CH3COOH is", "Ethanoic acid", ["Ethanol", "Methanoic acid", "Propanone"], "CH3COOH is a two-carbon carboxylic acid, so it is ethanoic acid."),
        ("The functional group present in CH3COCH3 is", "Ketone", ["Aldehyde", "Alcohol", "Ether"], "CH3COCH3 contains a carbonyl group between two carbons, which is a ketone.")
    ]
    prompt, correct, distractors, explanation = cases[occurrence % len(cases)]
    options = [correct] + distractors
    rng.shuffle(options)
    return _question(paper_id, question_number, "Chemistry", "Organic Basics", _difficulty(occurrence), prompt, options, options.index(correct), explanation, year)


def _hydrocarbons_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("hydrocarbon", paper_id, occurrence)
    cases = [
        ("The hybridization of each carbon atom in ethene is", "sp2", ["sp", "sp3", "dsp2"], "Each carbon in ethene forms three sigma bonds and one pi bond, so it is sp2 hybridized."),
        ("The hybridization of each carbon atom in ethyne is", "sp", ["sp2", "sp3", "dsp3"], "Each carbon in ethyne forms two sigma bonds and two pi bonds, so it is sp hybridized."),
        ("The number of pi bonds in ethyne is", "2", ["0", "1", "3"], "Ethyne contains a triple bond made of one sigma and two pi bonds."),
        ("The general formula of alkanes is", "CnH2n+2", ["CnH2n", "CnH2n-2", "CnHn"], "Saturated open-chain hydrocarbons follow the formula CnH2n+2.")
    ]
    prompt, correct, distractors, explanation = cases[occurrence % len(cases)]
    options = [correct] + distractors
    rng.shuffle(options)
    return _question(paper_id, question_number, "Chemistry", "Hydrocarbons", _difficulty(occurrence), prompt, options, options.index(correct), explanation, year)


def _polymers_biomolecules_question(paper_id: int, question_number: int, year: int, occurrence: int) -> PracticeQuestion:
    rng = _make_rng("polymer", paper_id, occurrence)
    cases = [
        ("The monomer used in the preparation of PVC is", "Vinyl chloride", ["Ethene", "Styrene", "Tetrafluoroethylene"], "PVC is formed by polymerisation of vinyl chloride."),
        ("Nylon-6,6 is prepared from", "hexamethylene diamine and adipic acid", ["ethylene glycol and terephthalic acid", "caprolactam only", "styrene"], "Nylon-6,6 is a condensation polymer of hexamethylene diamine and adipic acid."),
        ("Glucose is classified as a", "Monosaccharide", ["Disaccharide", "Polypeptide", "Lipid"], "Glucose is a single sugar unit, so it is a monosaccharide."),
        ("Proteins are polymers of", "Amino acids", ["Fatty acids", "Nucleotides", "Monosaccharides"], "Proteins are formed by peptide linkage between amino acids.")
    ]
    prompt, correct, distractors, explanation = cases[occurrence % len(cases)]
    options = [correct] + distractors
    rng.shuffle(options)
    return _question(paper_id, question_number, "Chemistry", "Polymers and Biomolecules", _difficulty(occurrence), prompt, options, options.index(correct), explanation, year)


MATH_BLUEPRINT = [
    _progression_question,
    _quadratic_question,
    _binomial_question,
    _trigonometry_question,
    _coordinate_question,
    _circle_question,
    _straight_line_question,
    _matrix_question,
    _probability_question,
    _permutation_question,
    _limit_question,
    _derivative_question,
    _integral_question,
    _vector_question,
    _complex_number_question,
    _parabola_question
]

PHYSICS_BLUEPRINT = [
    _kinematics_question,
    _newton_question,
    _work_energy_question,
    _shm_question,
    _gravitation_question,
    _thermodynamics_question,
    _electrostatics_question,
    _current_electricity_question,
    _magnetism_question,
    _optics_question
]

CHEMISTRY_BLUEPRINT = [
    _atomic_structure_question,
    _periodic_trends_question,
    _bonding_question,
    _thermochemistry_question,
    _equilibrium_question,
    _redox_question,
    _solutions_question,
    _organic_basics_question,
    _hydrocarbons_question,
    _polymers_biomolecules_question
]


def _build_subject_questions(
    paper_id: int,
    year: int,
    start_number: int,
    generators: List,
    questions_per_generator: int
) -> List[PracticeQuestion]:
    questions = []
    question_number = start_number

    for generator in generators:
        for occurrence in range(questions_per_generator):
            questions.append(generator(paper_id, question_number, year, occurrence))
            question_number += 1

    return questions


@lru_cache(maxsize=10)
def _generate_paper(paper_id: int) -> Dict:
    if paper_id < 1 or paper_id > len(PAST_PAPER_CYCLES):
        raise ValueError("Mock paper not found")

    paper_meta = PAST_PAPER_CYCLES[paper_id - 1]
    year = paper_meta["inspired_by_year"]

    math_questions = _build_subject_questions(paper_id, year, 1, MATH_BLUEPRINT, 5)
    physics_questions = _build_subject_questions(paper_id, year, 81, PHYSICS_BLUEPRINT, 4)
    chemistry_questions = _build_subject_questions(paper_id, year, 121, CHEMISTRY_BLUEPRINT, 4)

    questions = math_questions + physics_questions + chemistry_questions

    return {
        "paperId": paper_id,
        "title": paper_meta["title"],
        "inspiredByYear": year,
        "durationMinutes": OFFICIAL_PATTERN["duration_minutes"],
        "totalQuestions": OFFICIAL_PATTERN["total_questions"],
        "sections": OFFICIAL_PATTERN["sections"],
        "focus": paper_meta["focus"],
        "questions": questions
    }


def get_overview() -> Dict:
    return {
        "exam": OFFICIAL_PATTERN,
        "knowledgeBank": {
            "yearsCovered": [paper["inspired_by_year"] for paper in PAST_PAPER_CYCLES],
            "totalMockPapers": len(PAST_PAPER_CYCLES),
            "totalOriginalPracticeQuestions": OFFICIAL_PATTERN["total_questions"] * len(PAST_PAPER_CYCLES),
            "subjectBreakupAcrossBank": {
                "Mathematics": 80 * len(PAST_PAPER_CYCLES),
                "Physics": 40 * len(PAST_PAPER_CYCLES),
                "Chemistry": 40 * len(PAST_PAPER_CYCLES)
            },
            "topicCoverage": {
                "Mathematics": [
                    "Progressions",
                    "Quadratic Equations",
                    "Binomial Theorem",
                    "Trigonometry",
                    "Coordinate Geometry",
                    "Circles",
                    "Straight Lines",
                    "Matrices",
                    "Probability",
                    "Permutation and Combination",
                    "Limits",
                    "Differentiation",
                    "Integration",
                    "Vectors",
                    "Complex Numbers",
                    "Parabola"
                ],
                "Physics": [
                    "Kinematics",
                    "Newton's Laws",
                    "Work, Energy and Power",
                    "Simple Harmonic Motion",
                    "Gravitation",
                    "Thermodynamics",
                    "Electrostatics",
                    "Current Electricity",
                    "Magnetism",
                    "Ray Optics"
                ],
                "Chemistry": [
                    "Atomic Structure",
                    "Periodic Trends",
                    "Chemical Bonding",
                    "Thermochemistry",
                    "Chemical Equilibrium",
                    "Redox Reactions",
                    "Solutions",
                    "Organic Basics",
                    "Hydrocarbons",
                    "Polymers and Biomolecules"
                ]
            },
            "note": "Question distribution follows the official engineering paper model. Topic emphasis rotates across 2015-2024 mock cycles while keeping questions original and explanation-rich."
        },
        "mockPapers": list_mock_papers()
    }


def list_mock_papers() -> List[Dict]:
    papers = []
    for paper in PAST_PAPER_CYCLES:
        papers.append({
            "paperId": paper["paper_id"],
            "title": paper["title"],
            "inspiredByYear": paper["inspired_by_year"],
            "durationMinutes": OFFICIAL_PATTERN["duration_minutes"],
            "totalQuestions": OFFICIAL_PATTERN["total_questions"],
            "focus": paper["focus"]
        })
    return papers


def get_mock_paper(paper_id: int) -> Dict:
    paper = _generate_paper(paper_id)
    return {
        "paperId": paper["paperId"],
        "title": paper["title"],
        "inspiredByYear": paper["inspiredByYear"],
        "durationMinutes": paper["durationMinutes"],
        "totalQuestions": paper["totalQuestions"],
        "sections": paper["sections"],
        "focus": paper["focus"],
        "instructions": OFFICIAL_PATTERN["instructions"],
        "questions": [question.to_public_dict() for question in paper["questions"]]
    }


def get_solution_sheet(paper_id: int) -> Dict:
    paper = _generate_paper(paper_id)
    return {
        "paperId": paper["paperId"],
        "title": paper["title"],
        "inspiredByYear": paper["inspiredByYear"],
        "solutionSheet": [question.to_solution_dict() for question in paper["questions"]]
    }


def _normalize_answer(value) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        normalized = int(value)
    except (TypeError, ValueError):
        return None
    return normalized if 0 <= normalized <= 3 else None


def grade_mock_paper(paper_id: int, answers: Optional[Dict[str, int]]) -> Dict:
    paper = _generate_paper(paper_id)
    answers = answers or {}

    score = 0
    attempted = 0
    solutions = []
    subject_breakdown = {
        "Mathematics": {"correct": 0, "attempted": 0, "total": 80},
        "Physics": {"correct": 0, "attempted": 0, "total": 40},
        "Chemistry": {"correct": 0, "attempted": 0, "total": 40}
    }

    for question in paper["questions"]:
        selected = _normalize_answer(answers.get(question.id))
        if selected is not None:
            attempted += 1
            subject_breakdown[question.subject]["attempted"] += 1
        if selected == question.correct_option:
            score += 1
            subject_breakdown[question.subject]["correct"] += 1
        solutions.append(question.to_solution_dict(selected))

    for subject_stats in subject_breakdown.values():
        attempted_subject = subject_stats["attempted"]
        subject_stats["unanswered"] = subject_stats["total"] - attempted_subject
        subject_stats["accuracy"] = round((subject_stats["correct"] / attempted_subject) * 100, 2) if attempted_subject else 0.0

    unanswered = OFFICIAL_PATTERN["total_questions"] - attempted

    return {
        "paperId": paper["paperId"],
        "title": paper["title"],
        "inspiredByYear": paper["inspiredByYear"],
        "score": score,
        "maxScore": OFFICIAL_PATTERN["total_questions"],
        "attempted": attempted,
        "unanswered": unanswered,
        "accuracy": round((score / attempted) * 100, 2) if attempted else 0.0,
        "overallPercentage": round((score / OFFICIAL_PATTERN["total_questions"]) * 100, 2),
        "subjectBreakdown": subject_breakdown,
        "solutions": solutions
    }


def build_solution_sheet_email_content(result_payload: Dict, recipient_email: str) -> Dict[str, str]:
    subject = (
        f"TS EAPCET {result_payload['title']} solution sheet "
        f"and score summary"
    )

    subject_breakdown = result_payload.get("subjectBreakdown", {})
    solutions = result_payload.get("solutions", [])

    lines = [
        "TS EAPCET Engineering Mock Practice",
        "=" * 40,
        "",
        f"Recipient: {recipient_email}",
        f"Mock paper: {result_payload['title']}",
        f"Inspired by paper cycle: {result_payload['inspiredByYear']}",
        f"Score: {result_payload['score']} / {result_payload['maxScore']}",
        f"Attempted: {result_payload['attempted']}",
        f"Unanswered: {result_payload['unanswered']}",
        f"Accuracy: {result_payload['accuracy']}%",
        f"Overall percentage: {result_payload['overallPercentage']}%",
        "",
        "Subject breakdown",
        "-" * 40
    ]

    for subject, stats in subject_breakdown.items():
        lines.extend([
            f"{subject}:",
            f"  Correct: {stats['correct']}",
            f"  Attempted: {stats['attempted']}",
            f"  Unanswered: {stats['unanswered']}",
            f"  Accuracy: {stats['accuracy']}%",
            ""
        ])

    lines.extend([
        "Detailed solution sheet",
        "-" * 40
    ])

    for solution in solutions:
        selected_text = solution.get("selectedOptionText") or "Not answered"
        lines.extend([
            f"Q{solution['questionNumber']} | {solution['subject']} | {solution['topic']}",
            solution["prompt"],
            f"Your answer: {selected_text}",
            f"Correct answer: {solution['correctOptionText']}",
            f"Explanation: {solution['explanation']}",
            ""
        ])

    lines.extend([
        "Generated by JobDataCamp TS EAPCET practice module."
    ])

    return {
        "subject": subject,
        "body": "\n".join(lines)
    }
