# data-LLM

steps to deploy

go to terminal in a vm in gcloud


perform:
`docker-compose down`
`docker-compose up -d`

and then finally
`chmod +x script.sh`
`./script.sh`



to deploy using app engine:
    do: 
        gcloud app deploy

to setup CI/CD
    do:
        add deploy.yml file inside .github/workflows directory


CI/CD and app engine deployment aren't working as of now
DO MANUAL DEPLOYMENT FOR THE TIME BEING
