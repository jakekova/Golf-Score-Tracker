import express from 'express';
import fetch from 'node-fetch';

const app = express();
const PORT = 3000;

app.use(express.static('public'));
app.use(express.json());

app.post('/get-scores', async (req, res) => {
    const { golferNames } = req.body;

    try {
        const response = await fetch('http://localhost:5000/get-golf-scores');
        const data = await response.json();

        let totalScore = 0;
        for (const golfer of golferNames) {
            const golferData = data.leaderboard.find(player => player.name === golfer);
            if (golferData && golferData.score) {
                totalScore += golferData.score;
            }
        }

        res.json({ totalScore });
    } catch (error) {
        console.error('Error fetching scores:', error);
        res.status(500).json({ error: 'Failed to fetch scores' });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
