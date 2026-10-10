#!/usr/bin/env node
/**
 * 按模块生成类型别名文件（news.ts / user.ts / ...）
 *
 * 输入：packages/shared-types/openapi.json（由 pnpm api:fetch-openapi 产出）
 * 输出：packages/shared-types/src/<module>.ts + index.ts
 *
 * 归属规则：
 *   1. 路径形如 /api/<name>/... 的接口，其类型归入 <name> 模块；其余（如根路径 /）归入 common
 *   2. 沿 $ref 递归展开，得到每个模块真正用到的全部 schema（含嵌套引用）
 *   3. 被 2 个及以上模块用到的 schema 归入 common，避免同一类型在多处定义
 *
 * 别名文件只是 ./api.ts 的转出，类型源头始终唯一：
 *   export type NewsItem = components["schemas"]["NewsItem"];
 */

import { readFileSync, writeFileSync, readdirSync, rmSync } from "node:fs"
import { dirname, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const scriptDir = dirname(fileURLToPath(import.meta.url))
const pkgDir = resolve(scriptDir, "..")
const srcDir = join(pkgDir, "src")
const specPath = join(pkgDir, "openapi.json")

const MARKER = "gen-modules.mjs" // 用于识别本脚本的旧产物，可安全清理
const HEADER = [
  `// 本文件由 packages/shared-types/scripts/${MARKER} 自动生成，请勿手动修改。`,
  "// 重新生成：pnpm api:gen-types",
  "",
].join("\n")

const spec = JSON.parse(readFileSync(specPath, "utf8"))
const schemas = spec.components?.schemas ?? {}
const paths = spec.paths ?? {}

/** 递归收集节点里引用到的所有 #/components/schemas/* */
const collectRefs = (node, acc) => {
  if (Array.isArray(node)) {
    for (const item of node) collectRefs(item, acc)
  } else if (node && typeof node === "object") {
    if (typeof node.$ref === "string" && node.$ref.startsWith("#/components/schemas/")) {
      acc.add(node.$ref.slice("#/components/schemas/".length))
    }
    for (const value of Object.values(node)) collectRefs(value, acc)
  }
  return acc
}

/** /api/news/list -> news，/api/user -> user，/ -> common */
const moduleOf = (path) => {
  const matched = /^\/api\/([^/]+)/.exec(path)
  if (!matched) return "common"
  const name = matched[1]
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
  return /^[a-z]/.test(name) ? name : "common"
}

// 1. 每个模块直接引用到的 schema
const direct = new Map()
for (const [path, ops] of Object.entries(paths)) {
  const mod = moduleOf(path)
  if (!direct.has(mod)) direct.set(mod, new Set())
  collectRefs(ops, direct.get(mod))
}

// 2. 沿 $ref 展开成闭包
const closureOf = (seeds) => {
  const seen = new Set()
  const stack = [...seeds]
  while (stack.length) {
    const name = stack.pop()
    if (seen.has(name) || !(name in schemas)) continue
    seen.add(name)
    stack.push(...collectRefs(schemas[name], new Set()))
  }
  return seen
}

const perModule = new Map([...direct].map(([mod, seeds]) => [mod, closureOf(seeds)]))

// 3. 被多个模块引用的 schema 统一归 common
const owners = new Map()
for (const names of perModule.values()) {
  for (const name of names) owners.set(name, (owners.get(name) ?? 0) + 1)
}

const partitions = new Map()
const assign = (mod, name) => {
  if (!partitions.has(mod)) partitions.set(mod, new Set())
  partitions.get(mod).add(name)
}
for (const [mod, names] of perModule) {
  for (const name of names) {
    assign(mod !== "common" && owners.get(name) > 1 ? "common" : mod, name)
  }
}

// 4. 生成文件内容
const files = new Map()
const modules = [...partitions]
  .filter(([, names]) => names.size > 0)
  .map(([mod]) => mod)
  .sort()

for (const mod of modules) {
  const lines = [HEADER, 'import type { components } from "./api"', ""]
  for (const name of [...partitions.get(mod)].sort()) {
    lines.push(`export type ${name} = components["schemas"]["${name}"]`)
  }
  files.set(`${mod}.ts`, lines.join("\n") + "\n")
}

files.set(
  "index.ts",
  [
    HEADER,
    'export type * from "./api"',
    ...modules.map((mod) => `export type * from "./${mod}"`),
    "",
  ].join("\n"),
)

// 5. 清理上一轮生成但本轮已不存在的产物（只删带本脚本标记的文件，不动 api.ts）
for (const entry of readdirSync(srcDir)) {
  if (!entry.endsWith(".ts") || files.has(entry)) continue
  if (readFileSync(join(srcDir, entry), "utf8").includes(MARKER)) {
    rmSync(join(srcDir, entry))
    console.log(`🗑  清理已失效的分区文件 ${entry}`)
  }
}

for (const [name, content] of files) {
  writeFileSync(join(srcDir, name), content)
}

console.log(`✅ 按模块生成 ${files.size} 个文件：${[...files.keys()].join(", ")}`)
for (const mod of modules) {
  console.log(`   ${mod}.ts — ${partitions.get(mod).size} 个类型`)
}
