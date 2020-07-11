
redeploy_all: build_all deploy_all show_pods

build_all: crud_build timeline_build
create_all: crud_create timeline_create
deploy_all: crud_deploy timeline_deploy

redeploy_crud: crud_build crud_deploy show_pods
redeploy_timeline: timeline_build timeline_deploy show_pods

get_cluster:
	gcloud container clusters get-credentials super-brain --region us-central1 --project superbrain-282909

show_pods: get_cluster
	kubectl get pods

crud_build:
	docker build -t crud -f dockerfiles/crud.Dockerfile .
	docker tag crud gcr.io/superbrain-282909/crud
	docker push gcr.io/superbrain-282909/crud

timeline_build:
	docker build -t timeline -f dockerfiles/timeline.Dockerfile .
	docker tag timeline gcr.io/superbrain-282909/timeline
	docker push gcr.io/superbrain-282909/timeline

crud_create: get_cluster
	kubectl apply -f kubernetes/crud.yaml

crud_deploy: get_cluster
	kubectl patch deployment crud -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"date\":\"`date +'%s'`\"}}}}}"

timeline_create: get_cluster
	kubectl apply -f kubernetes/timeline.yaml

timeline_deploy: get_cluster
	kubectl patch deployment timeline -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"date\":\"`date +'%s'`\"}}}}}"
