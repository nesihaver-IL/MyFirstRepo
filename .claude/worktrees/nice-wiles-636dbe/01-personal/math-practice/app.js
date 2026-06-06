'use strict';

// ════════════════════════════════════════════════════════
//  UTILITIES
// ════════════════════════════════════════════════════════

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function gcd(a, b) {
  a = Math.abs(a); b = Math.abs(b);
  while (b) { [a, b] = [b, a % b]; }
  return a;
}

function lcm(a, b) {
  return (a / gcd(a, b)) * b;
}

/** Reduce a fraction {num, denom} to lowest terms */
function reduce(num, denom) {
  const g = gcd(Math.abs(num), Math.abs(denom));
  return { num: num / g, denom: denom / g };
}

/** Render a proper fraction as HTML */
function fracHTML(num, denom) {
  if (denom === 1) return `<span>${num}</span>`;
  return `<span class="frac"><span class="num">${num}</span><span class="den">${denom}</span></span>`;
}

/** Format a large number with commas (Hebrew style) */
function fmt(n) {
  return n.toLocaleString('he-IL');
}

// ════════════════════════════════════════════════════════
//  PHASE 3 — NATURAL NUMBERS MODULE
// ════════════════════════════════════════════════════════

/** Four basic operations, numbers up to 1,000,000 */
function genFourOps() {
  const ops = ['+', '−', '×', '÷'];
  const op  = ops[randomInt(0, 3)];

  let a, b, answer;

  if (op === '+') {
    a = randomInt(100, 999_999);
    b = randomInt(100, 1_000_000 - a);
    answer = a + b;
  } else if (op === '−') {
    b = randomInt(100, 500_000);
    a = randomInt(b, 999_999);
    answer = a - b;
  } else if (op === '×') {
    b = randomInt(2, 999);
    a = randomInt(2, Math.floor(999_999 / b));
    answer = a * b;
  } else {               // ÷
    b = randomInt(2, 100);
    const q = randomInt(2, 10_000);
    a = b * q;
    answer = q;
  }

  return {
    display: `<span>${fmt(a)}</span> <span>${op}</span> <span>${fmt(b)}</span> <span>=</span> <span>?</span>`,
    answer: String(answer),
    inputMode: 'numeric'
  };
}

/** Equations with unknown □: a OP □ = c  or  □ OP b = c */
function genEquation() {
  const ops  = ['+', '−', '×', '÷'];
  const op   = ops[randomInt(0, 3)];
  const side = randomInt(0, 1); // 0 = unknown on right, 1 = unknown on left

  let a, b, c, answer;

  if (op === '+') {
    b = randomInt(10, 9_999);
    c = randomInt(b + 10, 99_999);
    a = c - b;
    answer = side === 0 ? b : a;
  } else if (op === '−') {
    b = randomInt(10, 9_999);
    a = randomInt(b + 10, 99_999);
    c = a - b;
    if (side === 0) { answer = b; }
    else { a = c + b; answer = a; }
  } else if (op === '×') {
    b = randomInt(2, 99);
    c = randomInt(2, 999) * b;
    a = c / b;
    answer = side === 0 ? b : a;
  } else {          // ÷
    b = randomInt(2, 20);
    a = randomInt(2, 500) * b;
    c = a / b;
    answer = side === 0 ? b : a;
  }

  const box = `<span class="unknown">□</span>`;
  let display;
  if (side === 0) {
    display = `<span>${fmt(a)}</span> <span>${op}</span> ${box} <span>=</span> <span>${fmt(c)}</span>`;
  } else {
    display = `${box} <span>${op}</span> <span>${fmt(b)}</span> <span>=</span> <span>${fmt(c)}</span>`;
  }

  return { display, answer: String(answer), inputMode: 'numeric' };
}

/** Order of operations: a + b × c  or  (a + b) × c  or  a × b + c × d */
function genOrderOfOps() {
  const type = randomInt(0, 2);
  let display, answer;

  if (type === 0) {
    // a + b × c
    const b = randomInt(2, 50), c = randomInt(2, 50), a = randomInt(1, 200);
    answer = a + b * c;
    display = `${a} + ${b} × ${c} = ?`;
  } else if (type === 1) {
    // (a + b) × c
    const a = randomInt(1, 100), b = randomInt(1, 100), c = randomInt(2, 20);
    answer = (a + b) * c;
    display = `(${a} + ${b}) × ${c} = ?`;
  } else {
    // a × b − c ÷ d
    const d = randomInt(2, 10);
    const q = randomInt(1, 20);
    const c = d * q;
    const a = randomInt(2, 30), b = randomInt(2, 30);
    answer = a * b - c / d;
    if (Number.isInteger(answer) && answer > 0) {
      display = `${a} × ${b} − ${c} ÷ ${d} = ?`;
    } else {
      // fallback to simpler
      const b2 = randomInt(2, 50), c2 = randomInt(2, 50), a2 = randomInt(1, 200);
      answer = a2 + b2 * c2;
      display = `${a2} + ${b2} × ${c2} = ?`;
    }
  }

  return { display: `<span>${display}</span>`, answer: String(answer), inputMode: 'numeric' };
}

/** Inequalities: student chooses <, =, > */
function genInequality() {
  const type = randomInt(0, 2);
  let left, right;

  if (type === 0) {
    // plain numbers
    const base = randomInt(100, 99_999);
    const diff = randomInt(-500, 500);
    left  = base;
    right = base + diff;
  } else if (type === 1) {
    // expression vs number
    const a = randomInt(10, 500), b = randomInt(2, 20);
    left  = a * b;
    right = randomInt(left - 200, left + 200);
  } else {
    // two expressions
    const a = randomInt(2, 100), b = randomInt(2, 100);
    const c = randomInt(2, 100), d = randomInt(2, 100);
    left  = a + b;
    right = c + d;
  }

  const sign = left < right ? '<' : left > right ? '>' : '=';

  return {
    display: `<span>${fmt(left)}</span> <span style="color:var(--purple);font-size:1.2em">?</span> <span>${fmt(right)}</span>`,
    answer: sign,
    choices: ['<', '=', '>'],
    inputMode: 'choice'
  };
}

// ════════════════════════════════════════════════════════
//  PHASE 4 — FRACTIONS MODULE
// ════════════════════════════════════════════════════════

/** Pick a random proper fraction with denom ≤ maxDenom */
function genFraction(maxDenom = 12) {
  const denom = randomInt(2, maxDenom);
  const num   = randomInt(1, denom - 1);
  return reduce(num, denom);
}

/** Fraction of a quantity: (num/denom) × qty = whole number */
function genFracOfQty() {
  const denom = randomInt(2, 10);
  const num   = randomInt(1, denom - 1);
  const qty   = denom * randomInt(2, 20);   // guaranteed divisible
  const answer = (num / denom) * qty;

  const display = `
    ${fracHTML(num, denom)}
    <span> מתוך </span>
    <span>${qty}</span>
    <span> = ?</span>
  `;
  return { display, answer: String(answer), inputMode: 'numeric' };
}

/** Find the whole: (num/denom) of □ = part */
function genFindWhole() {
  const denom  = randomInt(2, 10);
  const num    = randomInt(1, denom - 1);
  const whole  = denom * randomInt(2, 20);
  const part   = (num / denom) * whole;

  const display = `
    ${fracHTML(num, denom)}
    <span> מ‑</span>
    <span class="unknown">□</span>
    <span> = </span>
    <span>${part}</span>
  `;
  return { display, answer: String(whole), inputMode: 'numeric' };
}

/** Add or subtract two fractions (same or inclusive denominators) */
function genFracAddSub() {
  const op = randomInt(0, 1) === 0 ? '+' : '−';

  // Pick two denominators where one divides the other (inclusive)
  const smallDenoms = [2, 3, 4, 5, 6, 8, 10, 12];
  const d1 = smallDenoms[randomInt(0, smallDenoms.length - 1)];
  // d2 is either equal to d1 or a multiple of d1
  const multiples = smallDenoms.filter(d => d % d1 === 0);
  const d2 = multiples[randomInt(0, multiples.length - 1)];

  const n1 = randomInt(1, d1 - 1);
  let n2   = randomInt(1, d2 - 1);

  // For subtraction ensure result > 0
  const common = lcm(d1, d2);
  let resNum = (op === '+')
    ? n1 * (common / d1) + n2 * (common / d2)
    : n1 * (common / d1) - n2 * (common / d2);

  if (op === '−' && resNum <= 0) {
    // swap so bigger fraction is first
    [n2] = [randomInt(1, n1 * (common / d1) / (common / d2) - 1) || 1];
    resNum = n1 * (common / d1) - n2 * (common / d2);
  }

  const { num: rn, denom: rd } = reduce(resNum, common);

  // Build answer string
  let answerStr;
  if (rd === 1) {
    answerStr = String(rn);
  } else if (rn > rd) {
    const whole = Math.floor(rn / rd);
    const rem   = rn % rd;
    answerStr = rem === 0 ? String(whole) : `${whole} ${rem}/${rd}`;
  } else {
    answerStr = `${rn}/${rd}`;
  }

  const display = `
    ${fracHTML(n1, d1)}
    <span> ${op} </span>
    ${fracHTML(n2, d2)}
    <span> = ?</span>
  `;

  return {
    display,
    answer: answerStr,
    hint: `כתוב שבר כ‑ מונה/מכנה (למשל 3/4) או מספר מעורב כ‑ 1 1/2`,
    inputMode: 'numeric'
  };
}

/** Mixed-number addition or subtraction */
function genMixedNumbers() {
  const op = randomInt(0, 1) === 0 ? '+' : '−';
  const smallDenoms = [2, 3, 4, 5, 6, 8, 10];
  const d1 = smallDenoms[randomInt(0, smallDenoms.length - 1)];
  const multiples = smallDenoms.filter(d => d % d1 === 0);
  const d2 = multiples[randomInt(0, multiples.length - 1)];

  const w1 = randomInt(1, 9), n1 = randomInt(1, d1 - 1);
  const w2 = randomInt(1, 6), n2 = randomInt(1, d2 - 1);

  const common = lcm(d1, d2);
  const totalNum1 = w1 * common + n1 * (common / d1);
  const totalNum2 = w2 * common + n2 * (common / d2);

  let resTotal = op === '+' ? totalNum1 + totalNum2 : totalNum1 - totalNum2;
  // Ensure positive result for subtraction
  if (resTotal <= 0) {
    resTotal = totalNum1 + totalNum2; // fall back to addition
  }

  const { num: rn, denom: rd } = reduce(resTotal, common);
  const wholeAns = Math.floor(rn / rd);
  const remAns   = rn % rd;

  let answerStr;
  if (remAns === 0) {
    answerStr = String(wholeAns);
  } else {
    const { num: fn, denom: fd } = reduce(remAns, rd);
    answerStr = `${wholeAns} ${fn}/${fd}`;
  }

  const mixed = (w, n, d) =>
    `<span>${w}</span>${fracHTML(n, d)}`;

  const display = `
    ${mixed(w1, n1, d1)}
    <span> ${op} </span>
    ${mixed(w2, n2, d2)}
    <span> = ?</span>
  `;

  return {
    display,
    answer: answerStr,
    hint: `כתוב מספר מעורב כ‑ 3 1/4 (שלם רווח מונה/מכנה)`,
    inputMode: 'numeric'
  };
}

// ════════════════════════════════════════════════════════
//  PHASE 5 — GEOMETRY MODULE
// ════════════════════════════════════════════════════════

/** Classify triangle by angles: acute / right / obtuse */
function genTriangleType() {
  const type = randomInt(0, 2); // 0=acute, 1=right, 2=obtuse
  let a, b, c;

  if (type === 1) {
    // right triangle: one angle = 90
    a = 90;
    b = randomInt(10, 80);
    c = 180 - a - b;
  } else if (type === 2) {
    // obtuse: one angle > 90
    a = randomInt(91, 150);
    b = randomInt(5, 180 - a - 5);
    c = 180 - a - b;
  } else {
    // acute: all < 90, sum = 180
    do {
      a = randomInt(30, 89);
      b = randomInt(30, 89);
      c = 180 - a - b;
    } while (c <= 0 || c >= 90);
  }

  const LABELS = {
    0: 'חד-זוויתי',
    1: 'ישר-זוויתי',
    2: 'קהה-זוויתי'
  };

  return {
    display: `<span>משולש עם זוויות:</span><br/><span>${a}°, ${b}°, ${c}°</span><br/><span>מהו סוג המשולש?</span>`,
    answer: LABELS[type],
    choices: ['חד-זוויתי', 'ישר-זוויתי', 'קהה-זוויתי'],
    inputMode: 'choice'
  };
}

/** Area of rectangle */
function genRectArea() {
  const l = randomInt(3, 50), w = randomInt(3, 50);
  const answer = l * w;
  return {
    display: `<span>מלבן באורך</span> <span>${l}</span> <span>ורוחב</span> <span>${w}</span><br/><span>מה שטחו?</span>`,
    answer: String(answer),
    inputMode: 'numeric'
  };
}

/** Area of triangle: ½ × base × height — always whole number */
function genTriArea() {
  // ensure base or height is even so ½ × b × h is integer
  const base   = randomInt(2, 40) * 2;  // always even
  const height = randomInt(2, 30);
  const answer = (base * height) / 2;
  return {
    display: `<span>משולש עם בסיס</span> <span>${base}</span> <span>וגובה</span> <span>${height}</span><br/><span>מה שטחו?</span>`,
    answer: String(answer),
    inputMode: 'numeric'
  };
}

// ════════════════════════════════════════════════════════
//  PHASE 6 — GAME ENGINE
// ════════════════════════════════════════════════════════

const GENERATORS = {
  fourOps:      genFourOps,
  equations:    genEquation,
  orderOfOps:   genOrderOfOps,
  inequalities: genInequality,
  fracOfQty:    genFracOfQty,
  findWhole:    genFindWhole,
  fracAddSub:   genFracAddSub,
  mixedNumbers: genMixedNumbers,
  triangleType: genTriangleType,
  rectArea:     genRectArea,
  triArea:      genTriArea,
};

const state = {
  module:   'numbers',
  topic:    'fourOps',
  correct:  0,
  total:    0,
  current:  null,   // { display, answer, inputMode, choices?, hint? }
  answered: false,
};

// DOM refs
const dom = {
  display:    document.getElementById('problem-display'),
  inputArea:  document.getElementById('input-area'),
  answerInput:document.getElementById('answer-input'),
  submitBtn:  document.getElementById('submit-btn'),
  choiceArea: document.getElementById('choice-area'),
  feedback:   document.getElementById('feedback'),
  nextBtn:    document.getElementById('next-btn'),
  resetBtn:   document.getElementById('reset-btn'),
  scoreCorr:  document.getElementById('score-correct'),
  scoreTotal: document.getElementById('score-total'),
};

// ── normalise answer for comparison ──
function normalise(str) {
  str = str.trim().replace(/\s+/g, ' ');
  // convert "3 1/4" to fraction: 13/4 for exact comparison
  // We store answers in the same format as we generate, so compare directly.
  return str;
}

function answersMatch(userRaw, correct) {
  const user = normalise(userRaw);
  const exp  = normalise(correct);
  if (user === exp) return true;

  // Accept commas as thousands separators in numeric answers
  const userNum = Number(user.replace(/,/g, ''));
  const expNum  = Number(exp.replace(/,/g, ''));
  if (!isNaN(userNum) && !isNaN(expNum)) return userNum === expNum;

  return false;
}

// ── Render ──
function loadProblem() {
  state.current  = GENERATORS[state.topic]();
  state.answered = false;

  dom.display.innerHTML = state.current.display;
  dom.feedback.textContent = '';
  dom.feedback.className   = '';
  dom.nextBtn.classList.add('hidden');
  dom.submitBtn.disabled = false;

  if (state.current.inputMode === 'choice') {
    dom.inputArea.classList.add('hidden');
    dom.choiceArea.classList.remove('hidden');
    dom.choiceArea.innerHTML = '';
    (state.current.choices || []).forEach(ch => {
      const btn = document.createElement('button');
      btn.className   = 'choice-btn';
      btn.textContent = ch;
      btn.addEventListener('click', () => handleChoiceAnswer(ch));
      dom.choiceArea.appendChild(btn);
    });
  } else {
    dom.choiceArea.classList.add('hidden');
    dom.inputArea.classList.remove('hidden');
    dom.answerInput.value = '';
    dom.answerInput.focus();
  }

  if (state.current.hint) {
    dom.feedback.textContent = `💡 ${state.current.hint}`;
    dom.feedback.className = '';
  }
}

function handleChoiceAnswer(choice) {
  if (state.answered) return;
  submitAnswer(choice);
}

function submitAnswer(choiceValue) {
  if (state.answered) return;
  state.answered = true;

  const userAnswer = choiceValue !== undefined
    ? choiceValue
    : dom.answerInput.value;

  const correct = answersMatch(userAnswer, state.current.answer);

  state.total++;
  if (correct) state.correct++;

  dom.scoreCorr.textContent  = state.correct;
  dom.scoreTotal.textContent = state.total;

  if (correct) {
    dom.feedback.textContent = '✓ כל הכבוד! תשובה נכונה 🎉';
    dom.feedback.className   = 'correct';
  } else {
    dom.feedback.innerHTML = `✗ לא נכון — התשובה היא: <strong>${state.current.answer}</strong>`;
    dom.feedback.className = 'wrong';
  }

  dom.submitBtn.disabled = true;
  // Disable choice buttons
  dom.choiceArea.querySelectorAll('.choice-btn').forEach(b => b.disabled = true);
  dom.nextBtn.classList.remove('hidden');
}

// ── Event listeners ──
dom.submitBtn.addEventListener('click', () => submitAnswer());

dom.answerInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') submitAnswer();
});

dom.nextBtn.addEventListener('click', loadProblem);

dom.resetBtn.addEventListener('click', () => {
  state.correct = 0;
  state.total   = 0;
  dom.scoreCorr.textContent  = '0';
  dom.scoreTotal.textContent = '0';
  loadProblem();
});

// Module tabs
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    state.module = btn.dataset.module;

    // Show matching subtopic group
    document.querySelectorAll('.subtopic-group').forEach(g => {
      g.classList.toggle('hidden', g.dataset.module !== state.module);
    });

    // Activate first sub-button of the new module
    const firstSub = document.querySelector(
      `.subtopic-group[data-module="${state.module}"] .sub-btn`
    );
    if (firstSub) {
      document.querySelectorAll('.sub-btn').forEach(b => b.classList.remove('active'));
      firstSub.classList.add('active');
      state.topic = firstSub.dataset.topic;
    }

    loadProblem();
  });
});

// Sub-topic buttons
document.querySelectorAll('.sub-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll(
      `.subtopic-group[data-module="${state.module}"] .sub-btn`
    ).forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    state.topic = btn.dataset.topic;
    loadProblem();
  });
});

// ── Boot ──
loadProblem();
