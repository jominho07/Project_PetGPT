const messages = [
    "함께한 시간은 소중한 추억으로 남습니다.",
    "사랑은 기억 속에서 계속됩니다.",
    "소중한 가족과의 추억은 사라지지 않습니다.",
    "반려동물은 언제나 마음속에서 함께합니다."
];

const randomMessage =
    messages[Math.floor(Math.random() * messages.length)];

document.getElementById("message").innerText = randomMessage;

