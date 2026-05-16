// ── Contadores das colunas ──────────────────────────────────────
function updateKanbanCounts() {
    ['pendente', 'em_progresso', 'concluída'].forEach(status => {
        const col   = document.getElementById('col-' + status);
        const count = document.getElementById('count-' + status);
        if (col && count) {
            count.textContent = col.querySelectorAll('.kanban-card').length;
        }
    });
}

updateKanbanCounts();

// ── SortableJS — drag and drop (apenas desktop no dashboard) ────
function initKanban() {
    const isMobile = window.innerWidth <= 768;
    const columns = ['pendente', 'em_progresso', 'concluída'];

    columns.forEach(status => {
        const col = document.getElementById('col-' + status);
        if (!col) return;

        Sortable.create(col, {
            group: 'kanban',
            animation: 150,
            ghostClass: 'kanban-ghost',
            chosenClass: 'kanban-chosen',
            dragClass: 'kanban-dragging',
            disabled: isMobile,

            onEnd: async function(evt) {
                const card      = evt.item;
                const taskId    = card.dataset.id;
                const newStatus = evt.to.id.replace('col-', '');
                const oldStatus = card.dataset.status;

                if (oldStatus === newStatus) return;

                card.dataset.status = newStatus;
                card.classList.remove('kanban-card-pend', 'kanban-card-prog', 'kanban-card-done');
                if (newStatus === 'concluída')    card.classList.add('kanban-card-done');
                if (newStatus === 'em_progresso') card.classList.add('kanban-card-prog');
                if (newStatus === 'pendente')     card.classList.add('kanban-card-pend');
                updateKanbanCounts();

                // Sincroniza o card na vista de lista
                const listCard = document.querySelector(`.task-card[data-id="${taskId}"]`);
                if (listCard) {
                    listCard.dataset.status = newStatus;

                    listCard.classList.remove('completed-card', 'progress-card', 'overdue-card', 'warning-card');
                    if (newStatus === 'concluída')   listCard.classList.add('completed-card');
                    if (newStatus === 'em_progresso') listCard.classList.add('progress-card');

                    const badge = listCard.querySelector('.tb-pend, .tb-done, .tb-progress');
                    if (badge) {
                        if (newStatus === 'concluída') {
                            badge.className = 'tb tb-done';
                            badge.innerText = '✓ Concluída';
                        } else if (newStatus === 'em_progresso') {
                            badge.className = 'tb tb-progress';
                            badge.innerText = '🔄 Em progresso';
                        } else {
                            badge.className = 'tb tb-pend';
                            badge.innerText = '⏳ Pendente';
                        }
                    }

                    // Remove botão concluir se foi para concluída
                    if (newStatus === 'concluída') {
                        const completeBtn = listCard.querySelector('.complete-btn');
                        if (completeBtn) completeBtn.remove();
                    }
                }

                try {
                    const res = await fetch(`/task/${taskId}/update-status`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ status: newStatus })
                    });

                    if (!res.ok) {
                        showToast('Erro ao mover tarefa.', 'error');
                        card.dataset.status = oldStatus;
                    } else {
                        showToast('Tarefa movida!', 'success');
                    }
                } catch {
                    showToast('Erro de conexão.', 'error');
                    card.dataset.status = oldStatus;
                }
            }
        });
    });
}

// Inicializa o Kanban quando o SortableJS estiver carregado
if (typeof Sortable !== 'undefined') {
    initKanban();
} else {
    document.addEventListener('DOMContentLoaded', initKanban);
}

// ── Filtros da lista ────────────────────────────────────────────
const filterButtons   = document.querySelectorAll('.filter-btn');
const priorityButtons = document.querySelectorAll('.priority-filter-btn');
const deadlineButtons = document.querySelectorAll('.deadline-filter-btn');
const taskCards       = document.querySelectorAll('.task-card');
const searchInput     = document.getElementById('search-input');
const sortSelect      = document.getElementById('sort-select');

let currentStatusFilter   = 'all';
let currentPriorityFilter = 'all';
let currentSort           = 'important';
let currentDeadlineFilter = 'all';

function sortTasks() {
    const tasksContainer = document.querySelector('.db-tasks-grid');
    if (!tasksContainer) return;

    const cards = Array.from(document.querySelectorAll('.task-card'));
    const priorityOrder = { alta: 1, media: 2, baixa: 3 };

    cards.sort((a, b) => {
        const priorityA = priorityOrder[a.dataset.priority] || 4;
        const priorityB = priorityOrder[b.dataset.priority] || 4;
        const dueA      = a.dataset.dueDate || '9999-12-31';
        const dueB      = b.dataset.dueDate || '9999-12-31';
        const createdA  = a.dataset.createdAt;
        const createdB  = b.dataset.createdAt;
        const statusA   = a.dataset.status;
        const statusB   = b.dataset.status;

        if (currentSort === 'important') {
            return (
                (statusA === 'concluída') - (statusB === 'concluída') ||
                priorityA - priorityB ||
                dueA.localeCompare(dueB)
            );
        }
        if (currentSort === 'due_date') return dueA.localeCompare(dueB);
        if (currentSort === 'priority')  return priorityA - priorityB;
        if (currentSort === 'newest')    return createdB.localeCompare(createdA);
        if (currentSort === 'oldest')    return createdA.localeCompare(createdB);
        return 0;
    });

    cards.forEach(card => tasksContainer.appendChild(card));
}

function applyFilters() {
    let visibleCards = 0;
    sortTasks();

    const searchText = searchInput ? searchInput.value.toLowerCase() : '';

    taskCards.forEach(card => {
        const status      = card.dataset.status;
        const priority    = card.dataset.priority;
        const overdue     = card.dataset.overdue.trim();
        const dueDate     = card.dataset.dueDate;
        const today       = card.dataset.today;
        const title       = card.dataset.title || '';
        const description = card.dataset.description || '';

        const statusMatch =
            currentStatusFilter === 'all' ||
            (currentStatusFilter === 'pending'   && status === 'pendente') ||
            (currentStatusFilter === 'progress'  && status === 'em_progresso') ||
            (currentStatusFilter === 'completed' && status === 'concluída') ||
            (currentStatusFilter === 'overdue'   && overdue === 'true');

        const priorityMatch =
            currentPriorityFilter === 'all' ||
            priority === currentPriorityFilter;

        const deadlineMatch =
            currentDeadlineFilter === 'all' ||
            (currentDeadlineFilter === 'overdue' && dueDate && dueDate < today && status !== 'concluída') ||
            (currentDeadlineFilter === 'today'   && dueDate === today && status !== 'concluída') ||
            (currentDeadlineFilter === 'future'  && dueDate && dueDate > today && status !== 'concluída') ||
            (currentDeadlineFilter === 'none'    && !dueDate);

        const searchMatch =
            title.includes(searchText) ||
            description.includes(searchText);

        if (statusMatch && priorityMatch && deadlineMatch && searchMatch) {
            card.style.display = '';
            visibleCards++;
        } else {
            card.style.display = 'none';
        }
    });

    const emptyMessage = document.getElementById('empty-filter-message');
    if (emptyMessage) {
        emptyMessage.style.display = visibleCards === 0 ? 'block' : 'none';
    }

    const tasksBg = document.querySelector('.db-tasks-bg');
    if (tasksBg) {
        tasksBg.style.display = visibleCards === 0 ? 'none' : '';
    }
}

filterButtons.forEach(button => {
    button.addEventListener('click', () => {
        filterButtons.forEach(btn => btn.classList.remove('active-filter'));
        button.classList.add('active-filter');
        currentStatusFilter = button.dataset.filter;
        applyFilters();
    });
});

priorityButtons.forEach(button => {
    button.addEventListener('click', () => {
        priorityButtons.forEach(btn => btn.classList.remove('active-priority'));
        button.classList.add('active-priority');
        currentPriorityFilter = button.dataset.priority;
        applyFilters();
    });
});

deadlineButtons.forEach(button => {
    button.addEventListener('click', () => {
        deadlineButtons.forEach(btn => btn.classList.remove('active-deadline'));
        button.classList.add('active-deadline');
        currentDeadlineFilter = button.dataset.deadline;
        applyFilters();
    });
});

if (searchInput) searchInput.addEventListener('input', applyFilters);

if (sortSelect) {
    sortSelect.addEventListener('change', () => {
        currentSort = sortSelect.value;
        sortTasks();
        applyFilters();
    });
}

// ── Concluir tarefa (lista) ─────────────────────────────────────
document.querySelectorAll('.complete-btn').forEach(button => {
    button.addEventListener('click', async () => {
        const url = button.dataset.url;
        await fetch(url);

        const card = button.closest('.task-card');
        card.classList.remove('overdue-card', 'warning-card', 'progress-card');
        card.classList.add('completed-card');
        card.dataset.status  = 'concluída';
        card.dataset.overdue = 'false';

        const statusBadge = card.querySelector('.tb-pend, .tb-progress');
        if (statusBadge) {
            statusBadge.className = 'tb tb-done';
            statusBadge.innerText = '✓ Concluída';
        }

        button.remove();
        showToast('Tarefa concluída!', 'success');
        applyFilters();
    });
});

// ── Toast ───────────────────────────────────────────────────────
function showToast(message, category) {
    const container = document.createElement('div');
    container.className = 'toast-container';

    const toast = document.createElement('div');
    toast.className = `toast ${category}`;
    toast.innerText = message;

    container.appendChild(toast);
    document.body.appendChild(container);

    setTimeout(() => container.remove(), 3500);
}

// ── Kanban mobile move menu ─────────────────────────────────────
function toggleMoveMenu(btn) {
    const card = btn.closest('.kanban-card');
    const menu = card.querySelector('.k-move-menu');
    document.querySelectorAll('.k-move-menu.open').forEach(m => {
        if (m !== menu) m.classList.remove('open');
    });
    menu.classList.toggle('open');
}

async function moveCardMobile(optionBtn, newStatus) {
    const card      = optionBtn.closest('.kanban-card');
    const menu      = card.querySelector('.k-move-menu');
    const taskId    = card.dataset.id;
    const oldStatus = card.dataset.status;

    menu.classList.remove('open');

    const destCol = document.getElementById('col-' + newStatus);
    if (!destCol) return;

    card.style.opacity    = '0';
    card.style.transform  = 'scale(0.95)';
    card.style.transition = 'opacity 0.2s, transform 0.2s';

    setTimeout(() => {
        destCol.appendChild(card);
        card.dataset.status = newStatus;
        card.classList.remove('kanban-card-pend', 'kanban-card-prog', 'kanban-card-done');
        if (newStatus === 'concluída')    card.classList.add('kanban-card-done');
        if (newStatus === 'em_progresso') card.classList.add('kanban-card-prog');
        if (newStatus === 'pendente')     card.classList.add('kanban-card-pend');
        if (typeof updateKanbanCounts === 'function') updateKanbanCounts();
        card.style.opacity   = '1';
        card.style.transform = 'scale(1)';
    }, 200);

    try {
        await fetch(`/task/${taskId}/update-status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        showToast('Tarefa movida!', 'success');
    } catch {
        showToast('Erro de conexão.', 'error');
    }
}

document.addEventListener('click', e => {
    if (!e.target.closest('.kanban-card')) {
        document.querySelectorAll('.k-move-menu.open').forEach(m => m.classList.remove('open'));
    }
});

// ── Mover card na lista ─────────────────────────────────────────
async function moveListCard(optionBtn, taskId, newStatus) {
    const card    = optionBtn.closest('.task-card');
    const menu    = card.querySelector('.k-move-menu');
    const oldStatus = card.dataset.status;

    menu.classList.remove('open');

    card.dataset.status = newStatus;

    // Atualiza classes visuais
    card.classList.remove('completed-card', 'progress-card', 'overdue-card', 'warning-card');
    if (newStatus === 'concluída')    card.classList.add('completed-card');
    if (newStatus === 'em_progresso') card.classList.add('progress-card');

    // Atualiza badge de status
    const badge = card.querySelector('.tb-pend, .tb-done, .tb-progress');
    if (badge) {
        if (newStatus === 'concluída') {
            badge.className = 'tb tb-done';
            badge.innerText = '✓ Concluída';
        } else if (newStatus === 'em_progresso') {
            badge.className = 'tb tb-progress';
            badge.innerText = '🔄 Em progresso';
        } else {
            badge.className = 'tb tb-pend';
            badge.innerText = '⏳ Pendente';
        }
    }

    // Remove botão concluir se foi para concluída
    if (newStatus === 'concluída') {
        const completeBtn = card.querySelector('.complete-btn');
        if (completeBtn) completeBtn.remove();
    }

    try {
        await fetch(`/task/${taskId}/update-status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        showToast('Status atualizado!', 'success');
        applyFilters();
    } catch {
        showToast('Erro de conexão.', 'error');
        card.dataset.status = oldStatus;
    }
}

// ── Confirmação de exclusão ─────────────────────────────────────
document.querySelectorAll('.ta-danger[href*="delete"]').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        const url = this.href;
        if (confirm('Tem certeza que deseja excluir esta tarefa? Esta ação não pode ser desfeita.')) {
            window.location.href = url;
        }
    });
});