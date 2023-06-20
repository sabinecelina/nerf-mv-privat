target "init" {
  dockerfile = "docker/Dockerfile.init"
}

target "dev" {
  dockerfile = "docker/Dockerfile.dev"
  contexts = {
    init = "target:init"
  }
}
