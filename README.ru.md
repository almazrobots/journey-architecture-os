# Journey Architecture OS — русская версия

**Journey Architecture OS — открытая операционная система для проектирования, измерения и управления путями клиентов и сотрудников (customer и employee journeys).**

Покрывает CJM, EJM, service design, journey management, governance, метрики и управление портфелем journeys. Поставляется как 15 вендор-нейтральных [Agent Skills](https://agentskills.io/specification) для ИИ-агентов и практиков.

Главная идея репозитория: перестать относиться к CJM/EJM как к красивой карте после воркшопа и сделать из journeys управляемую систему.

## Сквозной процесс

**Evidence → Actor → Journey Architecture → Current State → Service Blueprint → Moments that Matter → Metrics → Opportunities → Target Experience → Initiatives → Governance → Portfolio**

## Что отличает подход

- Любое существенное утверждение маркируется как `observed`, `inferred`, `hypothesis` или `unknown`.
- Journey имеет стабильный ID, владельца, версию, статус и дату ревью.
- CJM и EJM строятся от целей и реального опыта человека, а не от внутренней оргструктуры.
- Service Blueprint отделён от CJM: карта показывает опыт, blueprint — механизм его доставки.
- Метрики связываются с конкретными этапами и outcomes.
- Opportunity backlog связан с evidence, root causes, owner и инициативами.
- Journey portfolio позволяет управлять десятками и сотнями journeys на уровне компании.

## JourneyOps — операционный слой

Карта полезна, пока она актуальна. **JourneyOps** — часть системы, которая держит journeys живыми после картирования: владелец, версия, свежесть evidence, ритм ревью, метрики по этапам, связь opportunities с инициативами по всему портфелю. В репозитории это `journey-governance` + `journey-metrics` + `journey-portfolio-management`, а `journey-quality-audit` служит проверкой здоровья.

## Быстрый старт

Для широкого или неоднозначного запроса начинай с `experience-architecture`: он выбирает нужную последовательность остальных skills.

Для CJM:

`journey-architecture → journey-research → jobs-and-outcomes → customer-journey-mapping → moments-that-matter → journey-metrics → experience-opportunity-prioritization`

Для EJM:

`journey-architecture → journey-research → employee-journey-mapping → moments-that-matter → service-blueprinting → journey-metrics`

Для enterprise-модели:

`journey-architecture → journey-governance → journey-portfolio-management → journey-metrics → journey-quality-audit`

## Установка

```bash
python3 scripts/install_skills.py --all --target .agents/skills
```

Проверка:

```bash
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests
```

Основная документация написана на английском, чтобы репозиторий можно было публиковать международно. Методология не требует конкретного инструмента: её можно применять в Miro, FigJam, Smaply, spreadsheets, BI, Notion, Jira или собственной journey-management системе.
