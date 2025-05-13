document.addEventListener("DOMContentLoaded", () => {
    const activitiesContainer = document.getElementById("activities");
    const activityForm = document.getElementById("activityForm");
    const topicInput = document.getElementById("topic");
    const studyTimeInput = document.getElementById("study_time");
    const dateInput = document.getElementById("date");
    const clearHistoryButton = document.getElementById("clear-history");

    function loadActivities() {
        fetch("/activities")
            .then(response => response.json())
            .then(data => {
                activitiesContainer.innerHTML = ""; // Clear the container
                let totalMinutes = 0;
    
                data.forEach(activity => {
                    createActivity(activity);
                    totalMinutes += parseInt(activity.study_time);
                });
    
                document.getElementById("total-time").textContent = `Celkový čas štúdia: ${totalMinutes} minút`;
            })
            .catch(error => console.error("Error loading activities:", error));
    }
    

    function createActivity(activity) {
        const activityItem = document.createElement("li");

        activityItem.innerHTML = `
            <strong>${activity.topic}</strong> - ${activity.study_time} min 
            <br><strong>${new Date(activity.date).toLocaleString()}</strong>
            <button class="delete" onclick="deleteActivity(${activity.id})">X</button>
        `;

        activitiesContainer.appendChild(activityItem);
    }

    activityForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const topic = topicInput.value.trim();
        const study_time = studyTimeInput.value;
        const date = dateInput.value;

        if (topic && study_time && date) {
            fetch("/activities", {
                method: "POST",
                body: JSON.stringify({ topic, study_time, date }),
                headers: { "Content-Type": "application/json" }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(() => {
                loadActivities();
                topicInput.value = "";
                studyTimeInput.value = "";
                dateInput.value = "";
            })
            .catch(error => console.error("Error adding activity:", error));
        }
    });

    window.deleteActivity = (id) => {
        fetch(`/activities/${id}`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            loadActivities();
        })
        .catch(error => console.error("Error deleting activity:", error));
    };

    clearHistoryButton.addEventListener("click", () => {
        if (confirm("Naozaj chcete vymazať všetku históriu?")) {
            clearHistoryButton.disabled = true;
            clearHistoryButton.textContent = "Vymazávam...";

            fetch("/activities", {
                method: "DELETE",
                headers: { "Content-Type": "application/json" }
            })
            .then(response => {
                if (!response.ok) throw new Error("Failed to clear history");
                return response.json();
            })
            .then(data => {
                showToast(data.message || "História vymazaná");
                loadActivities();
            })
            .catch(error => {
                console.error("Error clearing history:", error);
                showToast("X Chyba pri mazaní histórie");
            })
            .finally(() => {
                clearHistoryButton.disabled = false;
                clearHistoryButton.textContent = "Vymazať Históriu";
            });
        }
    });

    function showToast(message) {
        const toast = document.createElement("div");
        toast.textContent = message;
        toast.style.position = "fixed";
        toast.style.bottom = "20px";
        toast.style.left = "50%";
        toast.style.transform = "translateX(-50%)";
        toast.style.background = "rgba(0,0,0,0.7)";
        toast.style.color = "#fff";
        toast.style.padding = "10px 20px";
        toast.style.borderRadius = "5px";
        toast.style.zIndex = "9999";
        toast.style.boxShadow = "0 2px 6px rgba(0,0,0,0.5)";
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    loadActivities();
});
