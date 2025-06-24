// Global variables
let currentEditingFinance = null
const finances = []

// API Base URL
const API_BASE = "http://localhost:5000"

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  initializeEventListeners()
  loadFinances()
})

function initializeEventListeners() {
  // Finance management
  document.getElementById("addFinanceBtn").addEventListener("click", () => openFinanceModal())
  document.getElementById("financeForm").addEventListener("submit", handleFinanceSubmit)

  // Month filter
  document.getElementById("monthFilter").addEventListener("change", filterByMonth)

  // Set default date to today
  document.getElementById("financeDate").value = new Date().toISOString().split("T")[0]
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

// Data loading
async function loadFinances() {
  try {
    const response = await fetch(`${API_BASE}/finances`)
    const finances = await response.json()

    renderFinanceList(finances)
    updateFinanceSummary(finances)
  } catch (error) {
    console.error("Erro ao carregar finanças:", error)
  }
}

async function filterByMonth() {
  const selectedMonth = document.getElementById("monthFilter").value

  if (!selectedMonth) {
    loadFinances()
    return
  }

  try {
    const response = await fetch(`${API_BASE}/finances/month/${selectedMonth}`)
    const finances = await response.json()

    renderFinanceList(finances)
    updateFinanceSummary(finances)
  } catch (error) {
    console.error("Erro ao filtrar por mês:", error)
  }
}

// Rendering functions
function renderFinanceList(finances) {
  const financeItems = document.getElementById("financeItems")
  financeItems.innerHTML = ""

  if (finances.length === 0) {
    financeItems.innerHTML =
      '<p style="text-align: center; color: #6c757d; padding: 2rem;">Nenhuma movimentação encontrada.</p>'
    return
  }

  finances.forEach((finance) => {
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

function updateFinanceSummary(finances) {
  const income = finances.filter((f) => f.value > 0).reduce((sum, f) => sum + f.value, 0)
  const expense = Math.abs(finances.filter((f) => f.value < 0).reduce((sum, f) => sum + f.value, 0))
  const balance = income - expense

  document.getElementById("totalIncome").textContent = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(income)

  document.getElementById("totalExpense").textContent = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(expense)

  document.getElementById("totalBalance").textContent = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(balance)
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
