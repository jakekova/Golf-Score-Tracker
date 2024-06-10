document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('golfers-form');
    const golfersInputs = document.getElementById('golfers-inputs');
    const totalScoreSpan = document.getElementById('total-score');

    // Generate 9 input fields
    for (let i = 0; i < 9; i++) {
        const input = document.createElement('input');
        input.type = 'text';
        input.placeholder = `Golfer ${i + 1} name`;
        input.required = true;
        golfersInputs.appendChild(input);
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const golferNames = Array.from(golfersInputs.querySelectorAll('input')).map(input => input.value.trim());

        if (golferNames.some(name => !name)) {
            alert('Please enter all golfer names.');
            return;
        }

        try {
            const response = await fetch('/get-scores', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ golferNames }),
            });

            if (!response.ok) {
                throw new Error('Failed to fetch scores');
            }

            const data = await response.json();
            totalScoreSpan.textContent = data.totalScore;
        } catch (error) {
            console.error('Error fetching scores:', error);
            alert('Error fetching scores. Please try again.');
        }
    });
});