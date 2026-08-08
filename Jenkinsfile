pipeline {
	agent any
	
	environment {
		OS4DEPOT_PASSPHRASE = credentials('AIOSTREAMS-OS4DEPOT-PASSPHRASE')
		DOCKER_IMAGE = "walkero/lha-on-docker:latest"
	}
	
	stages {
		stage('check-workspace') {
			steps {
				script {
					sh '''
						echo "=== Workspace location and contents ==="
						pwd
						ls -la
						echo ""
						echo "=== Git info ==="
						git status
						git log --oneline -5
					'''
				}
			}
		}

		stage('test-release-aiostreams') {
			when {
				allOf {
					branch 'master'
					not { buildingTag() }
				}
			}
			steps {
				script {
					sh '''
						mkdir -p aiostreams
						mv ./docs ./aiostreams/
						mv ./simplejson ./aiostreams/
						mv ./opentube ./aiostreams/
						mv ./*.py ./aiostreams/
						mv ./*.py.examples ./aiostreams/
						mv ./*.info ./aiostreams/
						mv ./*.md ./aiostreams/docs/
						mv LICENSE ./aiostreams/docs/
						sed -i "s/RELEASE_DATE/$(date +'"'"'%Y-%m-%d'"'"')/" ./aiostreams/docs/aiostreams.guide ./aiostreams/docs/CHANGELOG.md ./aiostreams/cmn.py
						sed -i "s/VERSION_TAG/TEST/" ./aiostreams/docs/aiostreams.guide ./aiostreams/docs/CHANGELOG.md ./aiostreams/cmn.py ./aminet.readme ./os4depot.readme
						lha -aq2o6 aiostreams-TEST.lha aiostreams/
						chmod 777 aiostreams-TEST.lha
					'''
				}
			}
			post {
				success {
					archiveArtifacts artifacts: 'aiostreams-TEST.lha', fingerprint: true
				}
			}
		}

		stage('release-aiostreams') {
			when {
				buildingTag()
			}
			steps {
				script {
					echo "Creating release archive for tag: ${TAG_NAME}"
					sh '''
						mkdir -p aiostreams
						mv ./docs ./aiostreams/
						mv ./simplejson ./aiostreams/
						mv ./opentube ./aiostreams/
						mv ./*.py ./aiostreams/
						mv ./*.py.examples ./aiostreams/
						mv ./*.info ./aiostreams/
						cp ./*.md ./aiostreams/docs/
						mv LICENSE ./aiostreams/docs/
						sed -i "s/RELEASE_DATE/$(date +'"'"'%Y-%m-%d'"'"')/" ./aiostreams/docs/aiostreams.guide ./aiostreams/docs/CHANGELOG.md ./aiostreams/cmn.py
						sed -i "s/VERSION_TAG/${TAG_NAME}/" ./aiostreams/docs/aiostreams.guide ./aiostreams/docs/CHANGELOG.md ./aiostreams/cmn.py ./aminet.readme ./os4depot.readme
						lha -aq2o6 aiostreams-${TAG_NAME}.lha aiostreams/
						chmod 777 aiostreams-${TAG_NAME}.lha
					'''
				}
			}
		}

		stage('deploy-on-github') {
			when {
				buildingTag()
			}
			steps {
				script {
					echo "Deploying to GitHub Releases"
					step([
						$class: 'GitHubReleaseNotifier',
						repositoryOwner: 'walkero-gr',
						repositoryName: 'aiostreams',
						tagName: env.TAG_NAME,
						releaseName: env.TAG_NAME,
						releaseBody: "${TAG_NAME} release",
						draft: false,
						prerelease: false,
						asset: "aiostreams-${TAG_NAME}.lha"
					])
				}
			}
		}

		stage('deploy-to-aminet') {
			when {
				buildingTag()
			}
			steps {
				script {
					echo "Preparing and uploading to Aminet"
					sh '''
						mkdir -p aminet-release
						cp aiostreams-${TAG_NAME}.lha ./aminet-release/aiostreams.lha
						cp aminet.readme ./aminet-release/aiostreams.readme
						chmod 777 -R aminet-release/
					'''
					ftpPublisher(
						continueOnError: false,
						failOnError: true,
						publishers: [
							[
								configName: 'Aminet FTP',
								transfers: [
									[
										sourceFiles: 'aminet-release/**',
										removePrefix: 'aminet-release/',
										remoteDirectory: './new',
										noDefaultExcludes: false,
										makeNeeded: true,
										patternsToExclude: '',
										cleanRemote: false,
										transferSet: true,
										asciiMode: false
									]
								],
								usePromotionTimestamp: false,
								useWorkspaceInPromotion: false,
								verbose: true
							]
						]
					)
				}
			}
		}

		stage('deploy-to-os4depot') {
			when {
				buildingTag()
			}
			steps {
				script {
					echo "Preparing and uploading to OS4Depot"
					sh '''
						mkdir -p os4depot-release
						cp aiostreams-${TAG_NAME}.lha ./os4depot-release/aiostreams.lha
						cp os4depot.readme ./os4depot-release/aiostreams_lha.readme
						sed -i "s/OS4DEPOT_PASSPHRASE/$OS4DEPOT_PASSPHRASE/" ./os4depot-release/aiostreams_lha.readme
						chmod 777 -R os4depot-release/
					'''
					ftpPublisher(
						continueOnError: false,
						failOnError: true,
						publishers: [
							[
								configName: 'OS4Depot FTP',
								transfers: [
									[
										sourceFiles: 'os4depot-release/**',
										removePrefix: 'os4depot-release/',
										remoteDirectory: './upload',
										noDefaultExcludes: false,
										makeNeeded: true,
										patternsToExclude: '',
										cleanRemote: false,
										transferSet: true,
										asciiMode: false
									]
								],
								usePromotionTimestamp: false,
								useWorkspaceInPromotion: false,
								verbose: true
							]
						]
					)
				}
			}
		}
	}

	post {
		always {
			cleanWs()
		}
	}
}
