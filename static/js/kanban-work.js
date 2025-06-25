// Global variables
let currentEditingTask = null
const tasks = []

// API Base URL
const API_BASE = ""
const TASK_TYPE = window.TASK_TYPE || "WORK"

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  initializeEventListeners()
  loadTasks()
})

function initializeEventListeners() {
  // Task management
  document.getElementById("addTaskBtn").addEventListener("click", () => openTaskModal())
  document.getElementById("taskForm").addEventListener("submit", handleTaskSubmit)

  // Drag and drop
  initializeDragAndDrop()
}

// Task management
function openTaskModal(task = null) {
  currentEditingTask = task
  const modal = document.getElementById("taskModal")
  const title = document.getElementById("taskModalTitle")

  if (task) {
    title.textContent = "Editar Tarefa Profissional"
    fillTaskForm(task)
  } else {
    title.textContent = "Nova Tarefa Profissional"
    document.getElementById("taskForm").reset()
  }

  modal.classList.add("active")
}

function fillTaskForm(task) {
  document.getElementById("taskTitle").value = task.title || ""
  document.getElementById("taskDescription").value = task.description || ""
  document.getElementById("taskPriority").value = task.priority || "MEDIUM"
  document.getElementById("taskDueDate").value = task.due_date || ""
  document.getElementById("taskAssigned").value = task.assigned_to || ""
  document.getElementById("taskTags").value = task.tags || ""
}

async function handleTaskSubmit(e) {
  e.preventDefault()

  const taskData = {
    title: document.getElementById("taskTitle").value,
    description: document.getElementById("taskDescription").value,
    priority: document.getElementById("taskPriority").value,
    type: TASK_TYPE,
    due_date: document.getElementById("taskDueDate").value,
    assigned_to: document.getElementById("taskAssigned").value,
    tags: document.getElementById("taskTags").value,
    created_by: "current_user",
  }

  try {
    let response
    if (currentEditingTask) {
      response = await fetch(`${API_BASE}/tasks/${currentEditingTask.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(taskData),
      })
    } else {
      response = await fetch(`${API_BASE}/tasks`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(taskData),
      })
    }

    const data = await response.json()

    if (response.ok) {
      closeModal("taskModal")
      loadTasks()
      alert(data.message)
    } else {
      alert("Erro ao salvar tarefa")
    }
  } catch (error) {
    console.error("Erro:", error)
    alert("Erro de conexão com o servidor")
  }
}

async function deleteTask(taskId) {
  if (!confirm("Tem certeza que deseja excluir esta tarefa profissional?")) return

  try {
    const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
      method: "DELETE",
    })

    const data = await response.json()

    if (response.ok) {
      loadTasks()
      alert(data.message)
    } else {
      alert("Erro ao excluir tarefa")
    }
  } catch (error) {
    console.error("Erro:", error)
    alert("Erro de conexão com o servidor")
  }
}

async function updateTaskStatus(taskId, newStatus) {
  try {
    const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ status: newStatus }),
    })

    if (response.ok) {
      loadTasks()
    }
  } catch (error) {
    console.error("Erro:", error)
  }
}

// Data loading
async function loadTasks() {
  try {
    const response = await fetch(`${API_BASE}/tasks/${TASK_TYPE.toLowerCase()}`)
    const tasks = await response.json()

    renderKanbanBoard(tasks)
  } catch (error) {
    console.error("Erro ao carregar tarefas:", error)
    // Fallback para dados mock se a API falhar
    renderKanbanBoard(getMockWorkTasks())
  }
}

function getMockWorkTasks() {
  return [
    {
      id: 4,
      title: "Desenvolver API de Usuários",
      description: "Criar endpoints para CRUD de usuários",
      status: "TO_DO",
      priority: "HIGH",
      type: "WORK",
      due_date: "2024-07-15",
      assigned_to: "Cliente ABC - Projeto Sistema",
      tags: "backend,api,urgente",
    },
    {
      id: 5,
      title: "Corrigir Bug no Frontend",
      description: "Resolver problema de responsividade",
      status: "IN_PROGRESS",
      priority: "MEDIUM",
      type: "WORK",
      due_date: "2024-07-18",
      assigned_to: "Equipe Frontend",
      tags: "frontend,bug,css",
    },
    {
      id: 6,
      title: "Deploy em Produção",
      description: "Fazer deploy da versão 2.0",
      status: "DONE",
      priority: "HIGH",
      type: "WORK",
      due_date: "2024-07-12",
      assigned_to: "DevOps Team",
      tags: "deploy,produção",
    },
  ]
}

// Rendering functions
function renderKanbanBoard(tasks) {
  const todoList = document.getElementById("todo-tasks")
  const progressList = document.getElementById("progress-tasks")
  const doneList = document.getElementById("done-tasks")

  // Clear existing tasks
  todoList.innerHTML = ""
  progressList.innerHTML = ""
  doneList.innerHTML = ""

  tasks.forEach((task) => {
    const taskElement = createTaskElement(task)

    switch (task.status) {
      case "TO_DO":
        todoList.appendChild(taskElement)
        break
      case "IN_PROGRESS":
        progressList.appendChild(taskElement)
        break
      case "DONE":
        doneList.appendChild(taskElement)
        break
    }
  })

  // Update task counts
  updateTaskCounts()
}

function createTaskElement(task) {
  const taskDiv = document.createElement("div")
  taskDiv.className = `task-card priority-${task.priority.toLowerCase()}`
  taskDiv.draggable = true
  taskDiv.dataset.taskId = task.id

  const tags = task.tags
    ? task.tags
        .split(",")
        .map((tag) => `<span class="task-tag work-tag">${tag.trim()}</span>`)
        .join("")
    : ""

  taskDiv.innerHTML = `
        <div class="task-actions">
            <button class="task-action" onclick="openTaskModal(${JSON.stringify(task).replace(/"/g, "&quot;")})">
                <i class="fas fa-edit"></i>
            </button>
            <button class="task-action" onclick="deleteTask(${task.id})">
                <i class="fas fa-trash"></i>
            </button>
        </div>
        <div class="task-title">${task.title}</div>
        <div class="task-description">${task.description || ""}</div>
        <div class="task-meta">
            <div class="task-tags">${tags}</div>
            <div>${task.due_date ? new Date(task.due_date).toLocaleDateString("pt-BR") : ""}</div>
        </div>
        ${task.assigned_to ? `<div class="task-assigned">💼 ${task.assigned_to}</div>` : ""}
    `

  // Add drag and drop functionality
  taskDiv.addEventListener("dragstart", handleDragStart)
  taskDiv.addEventListener("dragend", handleDragEnd)

  return taskDiv
}

function updateTaskCounts() {
  const todoCount = document.getElementById("todo-tasks").children.length
  const progressCount = document.getElementById("progress-tasks").children.length
  const doneCount = document.getElementById("done-tasks").children.length

  document.querySelector('[data-status="TO_DO"] .task-count').textContent = todoCount
  document.querySelector('[data-status="IN_PROGRESS"] .task-count').textContent = progressCount
  document.querySelector('[data-status="DONE"] .task-count').textContent = doneCount
}

// Drag and Drop functionality
function initializeDragAndDrop() {
  document.querySelectorAll(".kanban-column").forEach((column) => {
    column.addEventListener("dragover", handleDragOver)
    column.addEventListener("drop", handleDrop)
    column.addEventListener("dragenter", handleDragEnter)
    column.addEventListener("dragleave", handleDragLeave)
  })
}

function handleDragStart(e) {
  e.dataTransfer.setData("text/plain", e.target.dataset.taskId)
  e.target.classList.add("dragging")
}

function handleDragEnd(e) {
  e.target.classList.remove("dragging")
}

function handleDragOver(e) {
  e.preventDefault()
}

function handleDragEnter(e) {
  e.preventDefault()
  e.currentTarget.classList.add("drag-over")
}

function handleDragLeave(e) {
  e.currentTarget.classList.remove("drag-over")
}

function handleDrop(e) {
  e.preventDefault()
  e.currentTarget.classList.remove("drag-over")

  const taskId = e.dataTransfer.getData("text/plain")
  const newStatus = e.currentTarget.dataset.status

  updateTaskStatus(taskId, newStatus)
}

// Utility functions
function closeModal(modalId) {
  document.getElementById(modalId).classList.remove("active")
}

// Close modals when clicking outside
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal")) {
    e.target.classList.remove("active")
  }
})
