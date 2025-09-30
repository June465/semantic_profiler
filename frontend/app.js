const API_BASE_URL = 'http://localhost:8000'; // Your FastAPI backend URL

let uploadedResumeIds = []; // To store IDs of uploaded resumes
let latestEvaluationId = null; // To store the ID of the last evaluation

document.addEventListener('DOMContentLoaded', () => {
    updateResumeIdDisplay();
});

function updateResumeIdDisplay() {
    const displayDiv = document.getElementById('uploadedResumeIds');
    if (uploadedResumeIds.length > 0) {
        displayDiv.innerHTML = `**Uploaded Resume IDs:** ${uploadedResumeIds.join(', ')}`;
    } else {
        displayDiv.innerHTML = 'No resumes uploaded yet.';
    }
}

async function uploadResumes() {
    const fileInput = document.getElementById('resumeFileInput');
    const files = fileInput.files;

    if (files.length === 0) {
        alert('Please select at least one resume file.');
        return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('file', files[i]); // FastAPI expects 'file' as the field name
    }

    try {
        const response = await fetch(`${API_BASE_URL}/resumes/`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to upload resumes.');
        }

        const result = await response.json();
        // If backend returns a single ResumeResponse, convert to list for consistency
        const newResumeIds = Array.isArray(result) ? result.map(r => r.id) : [result.id];
        uploadedResumeIds.push(...newResumeIds);
        updateResumeIdDisplay();
        alert(`Successfully uploaded resume(s)! IDs: ${newResumeIds.join(', ')}`);

    } catch (error) {
        console.error('Error uploading resumes:', error);
        alert(`Error uploading resumes: ${error.message}`);
    }
}

async function evaluateCandidates() {
    const jobDescription = document.getElementById('jobDescriptionInput').value;

    if (!jobDescription.trim()) {
        alert('Please provide a job description.');
        return;
    }
    if (uploadedResumeIds.length === 0) {
        alert('Please upload resumes first before evaluating.');
        return;
    }

    const requestBody = {
        job_description: jobDescription,
        resume_ids: uploadedResumeIds,
        // job_title: "Optional Job Title" // You can add this if you have it
    };

    try {
        const response = await fetch(`${API_BASE_URL}/evaluations/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to evaluate candidates.');
        }

        const results = await response.json();
        if (results.length > 0) {
            latestEvaluationId = results[0].id; // Store ID of the first evaluation for demo
            alert(`Evaluation(s) complete! Latest Evaluation ID: ${latestEvaluationId}`);
            displayEvaluationResults(results);
        } else {
            alert('No evaluation results returned.');
        }

    } catch (error) {
        console.error('Error evaluating candidates:', error);
        alert(`Error evaluating candidates: ${error.message}`);
    }
}

async function fetchLatestEvaluation() {
    if (latestEvaluationId === null) {
        alert('No evaluations have been performed yet.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/evaluations/${latestEvaluationId}`);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch evaluation results.');
        }

        const result = await response.json();
        displayEvaluationResults([result]); // Display single result as a list

    } catch (error) {
        console.error('Error fetching evaluation results:', error);
        alert(`Error fetching evaluation results: ${error.message}`);
    }
}

function displayEvaluationResults(evaluations) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = ''; // Clear previous results

    if (evaluations.length === 0) {
        resultsDiv.innerHTML = '<p>No detailed evaluation results to display.</p>';
        return;
    }

    evaluations.forEach(evalResult => {
        const strengths = evalResult.strengths.map(s => `<li>${s}</li>`).join('');
        const weaknesses = evalResult.weaknesses.map(w => `<li>${w}</li>`).join('');

        resultsDiv.innerHTML += `
            <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #eee; border-radius: 5px;">
                <h3>Evaluation for Resume ID: ${evalResult.resume_id} (Score: ${evalResult.overall_score}/100)</h3>
                <p><strong>Summary:</strong> ${evalResult.summary}</p>
                <p><strong>Strengths:</strong></p>
                <ul>${strengths}</ul>
                <p><strong>Weaknesses:</strong></p>
                <ul>${weaknesses}</ul>
                <p><em>Evaluation ID: ${evalResult.id} on ${new Date(evalResult.evaluation_date).toLocaleString()}</em></p>
            </div>
        `;
    });
}