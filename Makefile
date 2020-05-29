
crud: crud_build crud_deploy

crud_create:
	az container create --image superbrain.azurecr.io/crud:latest --resource-group Super-Brain --name crud-server --ports 5000 --ip-address Public --registry-username superbrain --registry-password V6SxizYaaZi4=j4OoEGttIkKdWWv4dQG

crud_build:
	az acr build --image crud --registry superbrain --file dockerfiles/crud.Dockerfile .

crud_redeploy:
	az container restart --resource-group Super-Brain --name crud-server