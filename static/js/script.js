// Global variables
let currentUser = null
let isLoginMode = true
let currentEditingTask = null
let currentEditingFinance = null
const tasks = []
const finances = []

// API Base URL
const API_BASE = "http://localhost:5000"

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  initializeEventListeners()
  checkAuthStatus()
})

function initializeEventListeners() {
  // Auth form
  document.getElementById("authForm").addEventListener("submit", handleAuth)
  document.getElementById("authSwitchLink").addEventListener("click", toggleAuthMode)

  // Navigation
  document.querySelectorAll(".nav-tab").forEach((tab) => {
    tab.addEventListener("click", () => switchTab(tab.dataset.tab))
  })

  // Logout
  document.getElementById("logoutBtn").addEventListener("click", logout)

  // Task management
  document.getElementById("addTaskBtn").addEventListener("click", () => openTaskModal())
  document.getElementById("taskForm").addEventListener("submit", handleTaskSubmit)

  // Finance management
  document.getElementById("addFinanceBtn").addEventListener("click", () => openFinanceModal())
  document.getElementById("financeForm").addEventListener("submit", handleFinanceSubmit)

  // Set default date to today
  document.getElementById("financeDate").value = new Date().toISOString().split("T")[0]
}

// Authentication functions
async function handleAuth(e) {
  e.preventDefault()

  const username = document.getElementById("username").value
  const password = document.getElementById("password").value

  const endpoint = isLoginMode ? "/login" : "/register"

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    })

    const data = await response.json()

    if (response.ok) {
      if (isLoginMode) {
        currentUser = username
        showApp()
        loadData()
      } else {
        alert("Usuário registrado com sucesso! Faça login.")
        toggleAuthMode()
      }
    } else {
      alert(data.message || "Erro na autenticação")
    }
  } catch (error) {
    console.error("Erro:", error)
    alert("Erro de conexão com o servidor")
  }
}

function toggleAuthMode() {
  isLoginMode = !isLoginMode
  const title = document.getElementById("authTitle")
  const submitBtn = document.getElementById("authSubmit")
  const switchText = document.getElementById("authSwitchText")
  const switchLink = document.getElementById("authSwitchLink")

  if (isLoginMode) {
    title.textContent = "Login"
    submitBtn.textContent = "Entrar"
    switchText.textContent = "Não tem conta?"
    switchLink.textContent = "Registrar"
  } else {
    title.textContent = "Registrar"
    submitBtn.textContent = "Registrar"
    switchText.textContent = "Já tem conta?"
    switchLink.textContent = "Fazer Login"
  }

  // Clear form
  document.getElementById("authForm").reset()
}

function checkAuthStatus() {
  // In a real app, you'd check for stored session/token
  // For now, we'll just show the auth modal
}

function showApp() {
  document.getElementById("authModal").classList.remove("active")
  document.getElementById("app").classList.remove("hidden")
}

function logout() {
  currentUser = null
  document.getElementById("app").classList.add("hidden")
  document.getElementById("authModal").classList.add("active")
  document.getElementById("authForm").reset()
}

// Tab switching
function switchTab(tabName) {
  // Update nav tabs
  document.querySelectorAll(".nav-tab").forEach((tab) => {
    tab.classList.remove("active")
  })
  document.querySelector(`[data-tab="${tabName}"]`).classList.add("active")

  // Update tab content
  document.querySelectorAll(".tab-content").forEach((content) => {
    content.classList.remove("active")
  })
  document.getElementById(`${tabName}-tab`).classList.add("active")

  // Load data for the active tab
  if (tabName === "kanban") {
    loadTasks()
  } else if (tabName === "finance") {
    loadFinances()
  }
}

// Data loading
async function loadData() {
  await loadTasks()
  await loadFinances()
}

async function loadTasks() {
  try {
    // Since your API doesn't have a GET all tasks endpoint,
    // we'll simulate it or you can add one to your Flask app
    // For now, we'll use mock data and the existing tasks array
    renderKanbanBoard()
  } catch (error) {
    console.error("Erro ao carregar tarefas:", error)
  }
}

async function loadFinances() {
  try {
    // Similarly, we'll use mock data for finances
    // You might want to add a GET all finances endpoint
    renderFinanceList()
    updateFinanceSummary()
  } catch (error) {
    console.error("Erro ao carregar finanças:", error)
  }
}

// Task management
function openTaskModal(task = null) {
  currentEditingTask = task
  const modal = document.getElementById("taskModal")
  const title = document.getElementById("taskModalTitle")

  if (task) {
    title.textContent = "Editar Tarefa"
    fillTaskForm(task)
  } else {
    title.textContent = "Nova Tarefa"
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
    due_date: document.getElementById("taskDueDate").value,
    assigned_to: document.getElementById("taskAssigned").value,
    tags: document.getElementById("taskTags").value,
    created_by: currentUser,
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
  if (!confirm("Tem certeza que deseja excluir esta tarefa?")) return

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

// Finance management
function openFinanceModal(finance = null) {
  currentEditingFinance = finance
  const modal = document.getElementById("financeModal")
  const title = document.getElementById("financeModalTitle")

  if (finance) {
    title.textContent = "Editar Movimentação"
    fillFinanceForm(finance)
  } else {
    title.textContent = "Nova Movimentação"
    document.getElementById("financeForm").reset()
    document.getElementById("financeDate").value = new Date().toISOString().split("T")[0]
  }

  modal.classList.add("active")
}

function fillFinanceForm(finance) {
  document.getElementById("financeTitle").value = finance.title || ""
  document.getElementById("financeDescription").value = finance.description || ""
  document.getElementById("financeValue").value = finance.value || ""
  document.getElementById("financeDate").value = finance.transaction_date || ""
  document.getElementById("financeRecurrence").value = finance.recurrence || "NONE"
}

async function handleFinanceSubmit(e) {
  e.preventDefault()

  const financeData = {
    title: document.getElementById("financeTitle").value,
    description: document.getElementById("financeDescription").value,
    value: Number.parseFloat(document.getElementById("financeValue").value),
    transaction_date: document.getElementById("financeDate").value,
    recurrence: document.getElementById("financeRecurrence").value,
  }

  try {
    let response
    if (currentEditingFinance) {
      response = await fetch(`${API_BASE}/finances/${currentEditingFinance.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(financeData),
      })
    } else {
      response = await fetch(`${API_BASE}/finances`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(financeData),
      })
    }

    const data = await response.json()

    if (response.ok) {
      closeModal("financeModal")
      loadFinances()
      alert(data.message)
    } else {
      alert("Erro ao salvar movimentação")
    }
  } catch (error) {
    console.error("Erro:", error)
    alert("Erro de conexão com o servidor")
  }
}

async function deleteFinance(financeId) {
  if (!confirm("Tem certeza que deseja excluir esta movimentação?")) return

  try {
    const response = await fetch(`${API_BASE}/finances/${financeId}`, {
      method: "DELETE",
    })

    const data = await response.json()

    if (response.ok) {
      loadFinances()
      alert(data.message)
    } else {
      alert("Erro ao excluir movimentação")
    }
  } catch (error) {
    console.error("Erro:", error)
    alert("Erro de conexão com o servidor")
  }
}

// Rendering functions
function renderKanbanBoard() {
  const todoList = document.getElementById("todo-tasks")
  const progressList = document.getElementById("progress-tasks")
  const doneList = document.getElementById("done-tasks")

  // Clear existing tasks
  todoList.innerHTML = ""
  progressList.innerHTML = ""
  doneList.innerHTML = ""

  // Mock data for demonstration
  const mockTasks = [
    {
      id: 1,
      title: "Implementar autenticação",
      description: "Criar sistema de login e registro",
      status: "TO_DO",
      priority: "HIGH",
      due_date: "2024-01-15",
      assigned_to: "João",
      tags: "backend,segurança",
    },
    {
      id: 2,
      title: "Design da interface",
      description: "Criar mockups das telas principais",
      status: "IN_PROGRESS",
      priority: "MEDIUM",
      due_date: "2024-01-20",
      assigned_to: "Maria",
      tags: "frontend,design",
    },
    {
      id: 3,
      title: "Testes unitários",
      description: "Implementar testes para as APIs",
      status: "DONE",
      priority: "LOW",
      due_date: "2024-01-10",
      assigned_to: "Pedro",
      tags: "testes,qualidade",
    },
  ]

  mockTasks.forEach((task) => {
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
        .map((tag) => `<span class="task-tag">${tag.trim()}</span>`)
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
        ${task.assigned_to ? `<div class="task-assigned">👤 ${task.assigned_to}</div>` : ""}
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

function renderFinanceList() {
  const financeItems = document.getElementById("financeItems")
  financeItems.innerHTML = ""

  // Mock data for demonstration
  const mockFinances = [
    {
      id: 1,
      title: "Salário",
      description: "Salário mensal",
      value: 5000.0,
      transaction_date: "2024-01-01",
      recurrence: "MONTHLY",
    },
    {
      id: 2,
      title: "Aluguel",
      description: "Pagamento do aluguel",
      value: -1200.0,
      transaction_date: "2024-01-05",
      recurrence: "MONTHLY",
    },
    {
      id: 3,
      title: "Freelance",
      description: "Projeto de desenvolvimento",
      value: 2500.0,
      transaction_date: "2024-01-10",
      recurrence: "NONE",
    },
  ]

  mockFinances.forEach((finance) => {
    const financeElement = createFinanceElement(finance)
    financeItems.appendChild(financeElement)
  })
}

function createFinanceElement(finance) {
  const financeDiv = document.createElement("div")
  financeDiv.className = "finance-item"

  const isPositive = finance.value > 0
  const formattedValue = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(Math.abs(finance.value))

  financeDiv.innerHTML = `
        <div class="finance-info">
            <h4>${finance.title}</h4>
            <p>${finance.description || ""}</p>
            <p><small>${new Date(finance.transaction_date).toLocaleDateString("pt-BR")}</small></p>
        </div>
        <div class="finance-value ${isPositive ? "positive" : "negative"}">
            ${isPositive ? "+" : "-"}${formattedValue}
        </div>
        <div class="finance-actions">
            <button class="btn btn-secondary" onclick="openFinanceModal(${JSON.stringify(finance).replace(/"/g, "&quot;")})">
                <i class="fas fa-edit"></i>
            </button>
            <button class="btn btn-danger" onclick="deleteFinance(${finance.id})">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `

  return financeDiv
}

function updateFinanceSummary() {
  // Mock calculation - in real app, calculate from actual data
  const totalIncome = 7500.0
  const totalExpense = 1200.0
  const balance = totalIncome - totalExpense

  document.getElementById("totalIncome").textContent = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(totalIncome)

  document.getElementById("totalExpense").textContent = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(totalExpense)

  document.getElementById("totalBalance").textContent = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(balance)
}

// Drag and Drop functionality
function handleDragStart(e) {
  e.dataTransfer.setData("text/plain", e.target.dataset.taskId)
  e.target.classList.add("dragging")
}

function handleDragEnd(e) {
  e.target.classList.remove("dragging")
}

// Add drop zones
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".kanban-column").forEach((column) => {
    column.addEventListener("dragover", handleDragOver)
    column.addEventListener("drop", handleDrop)
    column.addEventListener("dragenter", handleDragEnter)
    column.addEventListener("dragleave", handleDragLeave)
  })
})

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

function formatCurrency(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value)
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("pt-BR")
}

// Close modals when clicking outside
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal")) {
    e.target.classList.remove("active")
  }
})
