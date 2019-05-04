workflow "on push" {
  on = "push"
  resolves = ["GitHub Action for Black"]
}

action "GitHub Action for Black" {
  uses = "lgeiger/black-action@master"
  args = ". --check"
}
