@echo off
cls

call git init -q data/diffusers/SD-2.0-4xUpscaler
cd data/diffusers/SD-2.0-4xUpscaler
call git lfs install
call git remote add -f origin https://huggingface.co/stabilityai/stable-diffusion-x4-upscaler
call git config core.sparseCheckout true
echo low_res_scheduler/ >> .git/info/sparse-checkout
echo scheduler/ >> .git/info/sparse-checkout
echo text_encoder/ >> .git/info/sparse-checkout
echo tokenizer/ >> .git/info/sparse-checkout
echo unet/ >> .git/info/sparse-checkout
echo vae/ >> .git/info/sparse-checkout
echo model_index.json >> .git/info/sparse-checkout
call git pull -q origin main
cd ../../..

echo Diffusers for SD-2.0-4xUpscaler installed