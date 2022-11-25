@echo off
cls

call git init -q data/diffusers/SD-1.5-VAE
cd data/diffusers/SD-1.5-VAE
call git lfs install
call git remote add -f origin https://huggingface.co/runwayml/stable-diffusion-v1-5
call git config core.sparseCheckout true
echo feature_extractor/ >> .git/info/sparse-checkout
echo safety_checker/ >> .git/info/sparse-checkout
echo scheduler/ >> .git/info/sparse-checkout
echo text_encoder/ >> .git/info/sparse-checkout
echo tokenizer/ >> .git/info/sparse-checkout
echo unet/ >> .git/info/sparse-checkout
echo vae/config.json >> .git/info/sparse-checkout
echo model_index.json >> .git/info/sparse-checkout
call git pull -q origin main
cd ../../..
echo Updating VAE
call git clone -q https://huggingface.co/stabilityai/sd-vae-ft-mse data/diffusers/updated-vae
copy /y .\data\diffusers\updated-vae\diffusion_pytorch_model.bin .\data\diffusers\SD-1.5-VAE\vae\diffusion_pytorch_model.bin

echo Diffusers for 1.5 with updated VAE installed