import { execSync } from "node:child_process";

const script = new URL("convert_publis.py", import.meta.url).pathname;

try {
  execSync(`python3 "${script}"`, { stdio: "inherit" });
} catch (e) {
  console.error("Publication generation failed:", e.message);
  process.exit(1);
}
