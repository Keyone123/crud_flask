// Global variables
let currentUser = null
let isLoginMode = true

// API Base URL - Usando a mesma origem para evitar CORS
const API_BASE = ""

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  initializeEventListeners()
  checkAuthStatus()
})

function initializeEventListeners() {
  // Auth form
  document.getElementById("authForm").addEventListener("submit", handleAuth)
  document.getElementById("authSwitchLink").addEventListener("click", toggleAuthMode)

  // Logout
  document.getElementById("logoutBtn").addEventListener("click", logout)
}

// Authentication functions
async function handleAuth(e) {
  e.preventDefault()

  const username = document.getElementById("username").value
  const password = document.getElementById("password").value

  const endpoint = isLoginMode ? "/login" : "/register"

  try {
    console.log(`Tentando ${isLoginMode ? "login" : "registro"} para usuário: ${username}`)

    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
      credentials: "same-origin",
    })

    console.log("Status da resposta:", response.status)

    if (!response.ok) {
      const errorData = await response.json()
      console.error("Erro de autenticação:", errorData)
      alert(errorData.message || "Erro na autenticação")
      return
    }

    const data = await response.json()
    console.log("Resposta do servidor:", data)

    if (isLoginMode) {
      currentUser = username
      showApp()
      loadDashboardData()
    } else {
      alert("Usuário registrado com sucesso! Faça login.")
      toggleAuthMode()
    }
  } catch (error) {
    console.error("Erro de conexão:", error)
    alert("Erro de conexão com o servidor. Verifique se o Flask está rodando.")
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

  document.getElementById("authForm").reset()
}

function checkAuthStatus() {
  // In a real app, you'd check for stored session/token
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

// Dashboard data loading
async function loadDashboardData() {
  try {
    await Promise.all([loadTasksSummary(), loadFinancesSummary(), loadRecentActivities(), loadUpcomingInstallments()])
  } catch (error) {
    console.error("Erro ao carregar dados do dashboard:", error)
  }
}

async function loadTasksSummary() {
  try {
    // Carregar tarefas da universidade
    const universityResponse = await fetch(`${API_BASE}/tasks/university`, {
      credentials: "same-origin",
    })

    // Carregar tarefas do trabalho
    const workResponse = await fetch(`${API_BASE}/tasks/work`, {
      credentials: "same-origin",
    })

    let universityTasks = []
    let workTasks = []

    if (universityResponse.ok) {
      universityTasks = await universityResponse.json()
    }

    if (workResponse.ok) {
      workTasks = await workResponse.json()
    }

    // Estatísticas da universidade
    const totalUniversityTasks = universityTasks.length
    const pendingUniversityTasks = universityTasks.filter((t) => t.status !== "DONE").length
    const completedUniversityTasks = universityTasks.filter((t) => t.status === "DONE").length

    document.getElementById("universityTasks").textContent = totalUniversityTasks
    document.getElementById("universityTasksSummary").textContent =
      `${pendingUniversityTasks} pendentes, ${completedUniversityTasks} concluídas`

    // Estatísticas do trabalho
    const totalWorkTasks = workTasks.length
    const pendingWorkTasks = workTasks.filter((t) => t.status !== "DONE").length
    const completedWorkTasks = workTasks.filter((t) => t.status === "DONE").length

    document.getElementById("workTasks").textContent = totalWorkTasks
    document.getElementById("workTasksSummary").textContent =
      `${pendingWorkTasks} pendentes, ${completedWorkTasks} concluídas`

    // Calcular produtividade
    const allTasks = [...universityTasks, ...workTasks]
    const thisWeekTasks = allTasks.filter((task) => {
      const taskDate = new Date(task.updated_at || task.created_at)
      const weekAgo = new Date()
      weekAgo.setDate(weekAgo.getDate() - 7)
      return taskDate >= weekAgo
    })

    const completedThisWeek = thisWeekTasks.filter((t) => t.status === "DONE").length
    const productivityScore =
      thisWeekTasks.length > 0 ? Math.round((completedThisWeek / thisWeekTasks.length) * 100) : 0

    document.getElementById("productivityScore").textContent = `${productivityScore}%`

    // Carregar tarefas recentes (misturadas)
    const recentTasks = allTasks.slice(-5).reverse()
    const recentTasksContainer = document.getElementById("recentTasks")
    recentTasksContainer.innerHTML = ""

    if (recentTasks.length === 0) {
      recentTasksContainer.innerHTML = '<p style="color: #6c757d; text-align: center;">Nenhuma tarefa encontrada</p>'
      return
    }

    recentTasks.forEach((task) => {
      const taskElement = document.createElement("div")
      taskElement.className = "activity-item"
      const typeIcon = task.type === "UNIVERSITY" ? "🎓" : "💼"
      taskElement.innerHTML = `
        <h4>${typeIcon} ${task.title}</h4>
        <p>Status: ${getStatusText(task.status)} | Prioridade: ${getPriorityText(task.priority)}</p>
      `
      recentTasksContainer.appendChild(taskElement)
    })
  } catch (error) {
    console.error("Erro ao carregar resumo de tarefas:", error)
    // Usar dados mock em caso de erro
    loadMockTasksSummary()
  }
}

function loadMockTasksSummary() {
  document.getElementById("universityTasks").textContent = "3"
  document.getElementById("universityTasksSummary").textContent = "2 pendentes, 1 concluída"
  document.getElementById("workTasks").textContent = "3"
  document.getElementById("workTasksSummary").textContent = "2 pendentes, 1 concluída"
  document.getElementById("productivityScore").textContent = "75%"

  const recentTasksContainer = document.getElementById("recentTasks")
  recentTasksContainer.innerHTML = `
    <div class="activity-item">
      <h4>🎓 Estudar para Prova de Cálculo</h4>
      <p>Status: A Fazer | Prioridade: Alta</p>
    </div>
    <div class="activity-item">
      <h4>💼 Desenvolver API de Usuários</h4>
      <p>Status: A Fazer | Prioridade: Alta</p>
    </div>
  `
}

async function loadFinancesSummary() {
  try {
    const response = await fetch(`${API_BASE}/finances`, {
      credentials: "same-origin",
    })

    if (!response.ok) {
      console.error("Erro ao carregar finanças:", response.status)
      return
    }

    const finances = await response.json()

    const currentMonth = new Date().getMonth() + 1
    const monthlyFinances = finances.filter((f) => {
      const financeMonth = new Date(f.transaction_date).getMonth() + 1
      return financeMonth === currentMonth
    })

    const income = monthlyFinances.filter((f) => f.value > 0).reduce((sum, f) => sum + f.value, 0)
    const expense = Math.abs(monthlyFinances.filter((f) => f.value < 0).reduce((sum, f) => sum + f.value, 0))
    const balance = income - expense

    document.getElementById("monthlyIncome").textContent = formatCurrency(income)
    document.getElementById("monthlyExpense").textContent = formatCurrency(expense)
    document.getElementById("monthlyBalance").textContent = formatCurrency(balance)

    // Load recent finances
    const recentFinances = finances.slice(-5).reverse()
    const recentFinancesContainer = document.getElementById("recentFinances")
    recentFinancesContainer.innerHTML = ""

    if (recentFinances.length === 0) {
      recentFinancesContainer.innerHTML =
        '<p style="color: #6c757d; text-align: center;">Nenhuma movimentação encontrada</p>'
      return
    }

    recentFinances.forEach((finance) => {
      const financeElement = document.createElement("div")
      financeElement.className = "activity-item"
      financeElement.innerHTML = `
        <h4>${finance.title}</h4>
        <p>${formatCurrency(finance.value)} | ${formatDate(finance.transaction_date)}</p>
      `
      recentFinancesContainer.appendChild(financeElement)
    })
  } catch (error) {
    console.error("Erro ao carregar resumo financeiro:", error)
    document.getElementById("recentFinances").innerHTML =
      '<p style="color: #dc3545; text-align: center;">Erro ao carregar finanças</p>'
  }
}

async function loadRecentActivities() {
  // This would load recent activities from both tasks and finances
  // For now, we'll use the data already loaded above
}

async function loadUpcomingInstallments() {
  try {
    const response = await fetch(`${API_BASE}/finances/upcoming-installments`, {
      credentials: "same-origin",
    })

    if (!response.ok) {
      console.error("Erro ao carregar parcelas:", response.status)
      return
    }

    const installments = await response.json()
    const container = document.getElementById("upcomingInstallments")
    container.innerHTML = ""

    if (installments.length === 0) {
      container.innerHTML = '<p style="color: #6c757d; text-align: center;">Nenhuma parcela pendente</p>'
      return
    }

    installments.slice(0, 5).forEach((installment) => {
      const installmentElement = document.createElement("div")
      installmentElement.className = "activity-item future-installment"
      installmentElement.innerHTML = `
        <h4>${installment.title}</h4>
        <p>${formatCurrency(installment.value)} | ${formatDate(installment.transaction_date)}
        <span class="installment-badge">${installment.installment_current}/${installment.installments_total}</span></p>
      `
      container.appendChild(installmentElement)
    })
  } catch (error) {
    console.error("Erro ao carregar parcelas:", error)
  }
}

// Utility functions
function getStatusText(status) {
  const statusMap = {
    TO_DO: "A Fazer",
    IN_PROGRESS: "Em Progresso",
    DONE: "Concluído",
  }
  return statusMap[status] || status
}

function getPriorityText(priority) {
  const priorityMap = {
    LOW: "Baixa",
    MEDIUM: "Média",
    HIGH: "Alta",
  }
  return priorityMap[priority] || priority
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

// Quick actions
function generateReport() {
  alert("Funcionalidade de relatório em desenvolvimento!")
}

function exportData() {
  alert("Funcionalidade de exportação em desenvolvimento!")
}

// Close modals when clicking outside
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal")) {
    e.target.classList.remove("active")
  }
})
