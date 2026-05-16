const filterButtons = document.querySelectorAll(".filter-btn");
const priorityButtons = document.querySelectorAll(".priority-filter-btn");
const deadlineButtons = document.querySelectorAll(".deadline-filter-btn");
const taskCards = document.querySelectorAll(".task-card");
const searchInput = document.getElementById("search-input");
const sortSelect = document.getElementById("sort-select");

let currentStatusFilter = "all";
let currentPriorityFilter = "all";
let currentSort = "important";
let currentDeadlineFilter = "all";

function sortTasks() {
    const tasksContainer = document.querySelector(".db-tasks-grid");
    if (!tasksContainer) return;

    const cards = Array.from(document.querySelectorAll(".task-card"));

    const priorityOrder = { alta: 1, media: 2, baixa: 3 };

    cards.sort((a, b) => {
        const statusA = a.dataset.status;
        const statusB = b.dataset.status;

        const priorityA = priorityOrder[a.dataset.priority] || 4;
        const priorityB = priorityOrder[b.dataset.priority] || 4;

        const dueA = a.dataset.dueDate || "9999-12-31";
        const dueB = b.dataset.dueDate || "9999-12-31";

        const createdA = a.dataset.createdAt;
        const createdB = b.dataset.createdAt;

        if (currentSort === "important") {
            return (
                (statusA === "concluída") - (statusB === "concluída") ||
                priorityA - priorityB ||
                dueA.localeCompare(dueB)
            );
        }
        if (currentSort === "due_date") return dueA.localeCompare(dueB);
        if (currentSort === "priority") return priorityA - priorityB;
        if (currentSort === "newest") return createdB.localeCompare(createdA);
        if (currentSort === "oldest") return createdA.localeCompare(createdB);

        return 0;
    });

    cards.forEach(card => tasksContainer.appendChild(card));
}

function applyFilters() {
    let visibleCards = 0;
    sortTasks();

    const searchText = searchInput ? searchInput.value.toLowerCase() : "";

    taskCards.forEach(card => {
        const status = card.dataset.status;
        const priority = card.dataset.priority;
        const overdue = card.dataset.overdue.trim();
        const dueDate = card.dataset.dueDate;
        const today = card.dataset.today;
        const title = card.dataset.title || "";
        const description = card.dataset.description || "";

        const statusMatch =
            currentStatusFilter === "all" ||
            (currentStatusFilter === "pending" && status === "pendente") ||
            (currentStatusFilter === "completed" && status === "concluída") ||
            (currentStatusFilter === "overdue" && overdue === "true");

        const priorityMatch =
            currentPriorityFilter === "all" ||
            priority === currentPriorityFilter;

        const deadlineMatch =
            currentDeadlineFilter === "all" ||
            (currentDeadlineFilter === "overdue" && dueDate && dueDate < today && status !== "concluída") ||
            (currentDeadlineFilter === "today" && dueDate === today && status !== "concluída") ||
            (currentDeadlineFilter === "future" && dueDate && dueDate > today && status !== "concluída") ||
            (currentDeadlineFilter === "none" && !dueDate);

        const searchMatch =
            title.includes(searchText) ||
            description.includes(searchText);

        if (statusMatch && priorityMatch && deadlineMatch && searchMatch) {
            card.style.display = "";
            visibleCards++;
        } else {
            card.style.display = "none";
        }
    });

    const emptyMessage = document.getElementById("empty-filter-message");
    if (emptyMessage) {
        emptyMessage.style.display = visibleCards === 0 ? "block" : "none";
    }

    const tasksBg = document.querySelector(".db-tasks-bg");
    if (tasksBg) {
        tasksBg.style.display = visibleCards === 0 ? "none" : "";
    }
}

filterButtons.forEach(button => {
    button.addEventListener("click", () => {
        filterButtons.forEach(btn => btn.classList.remove("active-filter"));
        button.classList.add("active-filter");
        currentStatusFilter = button.dataset.filter;
        applyFilters();
    });
});

priorityButtons.forEach(button => {
    button.addEventListener("click", () => {
        priorityButtons.forEach(btn => btn.classList.remove("active-priority"));
        button.classList.add("active-priority");
        currentPriorityFilter = button.dataset.priority;
        applyFilters();
    });
});

deadlineButtons.forEach(button => {
    button.addEventListener("click", () => {
        deadlineButtons.forEach(btn => btn.classList.remove("active-deadline"));
        button.classList.add("active-deadline");
        currentDeadlineFilter = button.dataset.deadline;
        applyFilters();
    });
});

if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
}

if (sortSelect) {
    sortSelect.addEventListener("change", () => {
        currentSort = sortSelect.value;
        sortTasks();
        applyFilters();
    });
}

const completeButtons = document.querySelectorAll(".complete-btn");

completeButtons.forEach(button => {
    button.addEventListener("click", async () => {
        const url = button.dataset.url;
        await fetch(url);

        const card = button.closest(".task-card");
        card.classList.remove("overdue-card", "warning-card");
        card.classList.add("completed-card");
        card.dataset.status = "concluída";
        card.dataset.overdue = "false";

        // Atualiza badge de status
        const statusBadge = card.querySelector(".tb-pend");
        if (statusBadge) {
            statusBadge.className = "tb tb-done";
            statusBadge.innerText = "✓ Concluída";
        }

        button.remove();

        showToast("Tarefa concluída!", "success");
        applyFilters();
    });
});

function showToast(message, category) {
    const container = document.createElement("div");
    container.className = "toast-container";

    const toast = document.createElement("div");
    toast.className = `toast ${category}`;
    toast.innerText = message;

    container.appendChild(toast);
    document.body.appendChild(container);

    setTimeout(() => container.remove(), 3500);
}