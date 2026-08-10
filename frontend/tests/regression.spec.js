import { expect, test } from '@playwright/test'

const PASSWORD = 'StrongPassword123!'

function uniqueEmail(prefix) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`
}

function toLocalDatetime(offsetMinutes) {
  const date = new Date(Date.now() + offsetMinutes * 60_000)
  const pad = (value) => String(value).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(
    date.getDate(),
  )}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

async function registerAndLogin(page, displayName) {
  const email = uniqueEmail(displayName.toLowerCase().replace(/\s+/g, '-'))

  await page.goto('/')
  await page.getByRole('button', { name: 'Create an account' }).click()
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Display name').fill(displayName)

  const passwords = page.locator('input[type="password"]')
  await passwords.nth(0).fill(PASSWORD)
  await passwords.nth(1).fill(PASSWORD)
  await page.getByRole('button', { name: 'Create account' }).click()

  await page.getByLabel('Email').fill(email)
  await page.locator('input[type="password"]').fill(PASSWORD)
  await page.getByRole('button', { name: 'Sign in' }).click()

  await expect(page.getByRole('heading', { name: `Hi ${displayName}!` })).toBeVisible()
}

async function addTodo(page, title, dueAt = '') {
  await page.getByLabel('New todo').fill(title)
  await page.getByLabel('Due date').fill(dueAt)
  await page.getByRole('button', { name: 'Add' }).click()
  await expect(page.locator('.todo-item', { hasText: title })).toBeVisible()
}

function todoItems(page, title) {
  return page.locator('.todo-item').filter({ hasText: title })
}

function todoItem(page, title) {
  return todoItems(page, title).first()
}

test('logs out back to the sign-in screen', async ({ page }) => {
  await registerAndLogin(page, 'Logout Tester')

  await page.getByRole('button', { name: 'Sign out' }).click()

  await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible()
})

test('sorts newest, oldest, and completed first', async ({ page }) => {
  await registerAndLogin(page, 'Sort Tester')

  await addTodo(page, 'Alpha task')
  await addTodo(page, 'Beta task')
  await addTodo(page, 'Gamma task')

  await expect(page.locator('.todo-title')).toHaveText([
    'Gamma task',
    'Beta task',
    'Alpha task',
  ])

  await page.getByLabel('Sort').selectOption('oldest')
  await expect(page.locator('.todo-title')).toHaveText([
    'Alpha task',
    'Beta task',
    'Gamma task',
  ])

  await page.getByLabel('Mark "Beta task" as complete').click()
  await page.getByLabel('Sort').selectOption('completed')

  await expect(page.locator('.todo-title')).toHaveText([
    'Beta task',
    'Gamma task',
    'Alpha task',
  ])
})

test('shows due dates, overdue status, and clearing due dates', async ({
  page,
}) => {
  await registerAndLogin(page, 'Due Date Tester')

  await addTodo(page, 'No due item')
  await addTodo(page, 'Future due item', toLocalDatetime(24 * 60))
  await addTodo(page, 'Past due item', toLocalDatetime(-24 * 60))

  const futureItem = page.locator('.todo-item', { hasText: 'Future due item' })
  const pastItem = page.locator('.todo-item', { hasText: 'Past due item' })

  await expect(futureItem).toContainText('Due ·')
  await expect(pastItem).toContainText('Overdue ·')

  await futureItem.getByRole('button', { name: /Edit/ }).click()
  await futureItem.getByRole('button', { name: 'Clear due date' }).click()
  await futureItem.getByRole('button', { name: 'Save' }).click()

  await expect(futureItem).not.toContainText('Due ·')
})

test('saves edits and cancels them with Escape', async ({ page }) => {
  await registerAndLogin(page, 'Edit Tester')

  await addTodo(page, 'Editable task')

  const item = todoItem(page, 'Editable task')

  await item.getByRole('button', { name: 'Edit "Editable task"' }).click()
  await item.getByRole('textbox', { name: 'Edit todo title' }).fill('Edited once')
  await page.keyboard.press('Escape')
  await expect(item).toContainText('Editable task')

  await item.getByRole('button', { name: 'Edit "Editable task"' }).click()
  await item.getByRole('textbox', { name: 'Edit todo title' }).fill('Edited once')
  await item.getByRole('button', { name: 'Save' }).click()

  await expect(todoItems(page, 'Editable task')).toHaveCount(0)
  await expect(todoItem(page, 'Edited once')).toBeVisible()
})

test('persists todos across refreshes and supports delete', async ({ page }) => {
  await registerAndLogin(page, 'Persistence Tester')

  await addTodo(page, 'Persistent task')

  await page.reload()
  await expect(todoItem(page, 'Persistent task')).toBeVisible()

  await todoItem(page, 'Persistent task')
    .getByRole('button', { name: 'Delete "Persistent task"' })
    .click()

  await expect(todoItems(page, 'Persistent task')).toHaveCount(0)

  await page.reload()
  await expect(todoItems(page, 'Persistent task')).toHaveCount(0)
})
