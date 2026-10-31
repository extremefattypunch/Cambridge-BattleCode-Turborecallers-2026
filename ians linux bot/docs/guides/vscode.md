<!-- source: https://2026a.battlecode.co.uk/game/docs/vscode -->
Handbook/Guides

# VSCode

3 min read · Current game rules

On this page

1. Install Visual Studio Code2. Open your bot folder3. Set up OCaml editing4. Build and test in the terminal

## 1. Install Visual Studio Code#

Download the desktop app for your operating system. The language selector at the top of this guide changes the extension and setup instructions, and remembers your choice.

Download Visual Studio Code →

Open the Extensions view using the blocks icon in the left Activity Bar. You will install the extension listed below for your language. Open the Command Palette with Ctrl+Shift+P on Windows/Linux or Cmd+Shift+P on macOS when a step asks you to run an editor command.

## 2. Open your bot folder#

Install the CAMBC CLI first if needed, then use `cambc init` to create a workspace. Select your language and include its starter bot. Enter the workspace directory printed by the CLI.

Download the CAMBC CLI →

Create a bot from the workspace directory

```
cambc new my-bot --lang ocaml
```

- In VS Code, choose File > Open Folder.
- Select `bots/my-bot` inside your CAMBC workspace. Open the whole bot folder, not just `src` or an individual file.
- Open `src/main.ml` in the Explorer.

You can instead open the generated starter at `bots/starter-ocaml`. Replace `my-bot` in the commands below with your bot's name. Keep the bot inside the CAMBC workspace: its editor settings refer to the SDK two directories above it.

Or open it from the workspace terminal

```
code bots/my-bot
```

If the code command is unavailable

File > Open Folder works without it. On macOS, the Command Palette command Shell Command: Install 'code' command in PATH enables the terminal shortcut.

## 3. Set up OCaml editing#

Install OCaml Platform (`ocamllabs.ocaml-platform`). The portable CLI can build your bot on its own, but editor completion also needs an OCaml language server. The starter is built by the CLI, not Dune, so configure its SDK interface explicitly.

Install OCaml Platform →

Install OCaml and opam →

After setting up opam and an OCaml switch, install the editor tools in that switch. In the Command Palette, run `OCaml: Select a Sandbox for this Workspace` and select the same switch.

Install editor tools

```
opam install ocaml-lsp-server dot-merlin-reader
```

In VS Code's Explorer, create `.cambc/editor` inside the bot folder. From the bot folder's terminal, compile the SDK interface with your editor's compiler. This avoids mixing the editor's compiled interfaces with the CLI's compiler version.

Run from bots/my-bot

```
opam exec -- ocamlc -c -o .cambc/editor/cambc.cmi ../../sdk/ocaml/cambc.mli
```

Create these two files in the bot folder. If `.vscode/settings.json` already exists, add the setting to its existing object.

.merlin

```
S src
S ../../sdk/ocaml
B .cambc/editor
```

.vscode/settings.json

```
{
  "ocaml.server.args": ["--fallback-read-dot-merlin"]
}
```

Reload the VS Code window and open `src/main.ml`. Hover over `Cambc` functions to check their types. Recompile the interface after refreshing the SDK. If you add your own modules, compile their interfaces into `.cambc/editor` with the same switch too; `S` paths find source, while `B` paths find compiled interfaces.

OCaml language server configuration →

## 4. Build and test in the terminal#

Choose Terminal > New Terminal. With the bot folder open, the terminal starts in `bots/my-bot`; the CLI finds the enclosing CAMBC workspace automatically. Save your edits before building.

Build the bot

```
cambc build my-bot
```

To keep replays together in the workspace, go up two directories before running a match:

Run against the generated starter

```
cd ../..
cambc run my-bot starter-ocaml -o replays --view
```

The CLI builds changed source and opens the replay after the match. A map must be available in `maps/`; refresh the platform's published pool with `cambc maps pull`. Use this workflow instead of the editor's generic Run or Debug button: the bot needs the CAMBC match runner.

Getting Started ↗

Create, test and submit a C++ bot with the CAMBC CLI.

Bot API reference ↗

Public C++ SDK functions, methods and camp-group state types.

← PreviousDistance Fields←→ turn pagesNext → · Bot APIBot API reference