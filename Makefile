.PHONY: image push

image:
	docker build -t lechuckroh/gitlab-migration .

push:
	docker push lechuckroh/gitlab-migration
