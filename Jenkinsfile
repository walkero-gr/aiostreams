pipeline {
    agent any
    
    environment {
        OS4DEPOT_PASSPHRASE = credentials('AIOSTREAMS-OS4DEPOT-PASSPHRASE')
        DOCKER_IMAGE = "walkero/lha-on-docker"
        GITHUB_TOKEN = credentials('github-access-token')
    }
    
    stages {
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
                        echo "Creating aiostreams directory..."
                        mkdir -p release/aiostreams
                        
                        echo "Moving files..."
                        mv ./docs ./release/aiostreams/
                        mv ./simplejson ./release/aiostreams/
                        mv ./opentube ./release/aiostreams/
                        mv ./*.py ./release/aiostreams/
                        mv ./*.py.examples ./release/aiostreams/
                        mv ./*.info ./release/aiostreams/
                        mv ./*.md ./release/aiostreams/docs/
                        mv LICENSE ./release/aiostreams/docs/
                        
                        echo "Running sed commands..."
                        sed -i "s/RELEASE_DATE/$(date +'%Y-%m-%d')/" ./release/aiostreams/docs/aiostreams.guide ./release/aiostreams/docs/CHANGELOG.md ./release/aiostreams/cmn.py
                        sed -i "s/VERSION_TAG/TEST/" ./release/aiostreams/docs/aiostreams.guide ./release/aiostreams/docs/CHANGELOG.md ./release/aiostreams/cmn.py ./aminet.readme ./os4depot.readme

                        echo "Creating LHA archive with Docker..."
                        cd ./release && lha aq ../aiostreams-TEST.lha ./*
                        
                        echo "Archive created successfully!"
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
                        echo "Creating aiostreams directory..."
                        mkdir -p release/aiostreams
                        
                        echo "Moving files..."
                        mv ./docs ./release/aiostreams/
                        mv ./simplejson ./release/aiostreams/
                        mv ./opentube ./release/aiostreams/
                        mv ./*.py ./release/aiostreams/
                        mv ./*.py.examples ./release/aiostreams/
                        mv ./*.info ./release/aiostreams/
                        cp ./*.md ./release/aiostreams/docs/
                        mv LICENSE ./release/aiostreams/docs/
                        
                        echo "Running sed commands..."
                        sed -i "s/RELEASE_DATE/$(date +'%Y-%m-%d')/" ./release/aiostreams/docs/aiostreams.guide ./release/aiostreams/docs/CHANGELOG.md ./release/aiostreams/cmn.py
                        sed -i "s/VERSION_TAG/${TAG_NAME}/" ./release/aiostreams/docs/aiostreams.guide ./release/aiostreams/docs/CHANGELOG.md ./release/aiostreams/cmn.py ./aminet.readme ./os4depot.readme

                        echo "Creating LHA archive..."
                        cd ./release && lha aq ../aiostreams-${TAG_NAME}.lha ./*
                        
                        echo "Archive created successfully!"
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
                    echo "Uploading to GitHub Release"
                    sh '''
                        echo "Uploading aiostreams-${TAG_NAME}.lha to release ${TAG_NAME}..."
                        export GH_TOKEN="${GITHUB_TOKEN_PSW}"
                        gh release upload ${TAG_NAME} ./aiostreams-${TAG_NAME}.lha \
                            --repo walkero-gr/aiostreams \
                            --clobber
                        echo "File uploaded successfully!"
                    '''
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
