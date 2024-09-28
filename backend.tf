terraform {
  backend "s3" {
    bucket = "sctp-ce6-tfstate"
    key    = "tommycs6-http-apigw.tfstate"
    region = "ap-southeast-1"
  }
}