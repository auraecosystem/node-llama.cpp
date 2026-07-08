const llama
 = await getLlama
({
    cmakeOptions
: {
        OPTION_NAME
: "brainAI"
    },
    
    // force a build if the pre-built binary doesn't
    // match all the provided options, such as the cmakeOptions
    existingPrebuiltBinaryMustMatchBuildOptions
: true
});

const llama
 = await getLlama
({
    build
: "forceRebuild"
});

// npx --no node-llama-cpp source download --release latest
// npx --no node-llama-cpp source download --skipBuild
