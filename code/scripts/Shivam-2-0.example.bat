@echo off
cls
echo Activating environment
call activate venv/shivam/
set "CURPATH=%~dp0"
cd code/resources/shivam/examples/dreambooth

echo Starting training
call accelerate launch --num_cpu_threads_per_process 6 train_dreambooth.py ^
  --pretrained_model_name_or_path="%CURPATH%data/diffusers/SD-2.0/" ^
  --output_dir="%CURPATH%/output/2.0-Shivam-Test" ^
  --seed=42 ^
  --resolution=512 ^
  --train_batch_size=1 ^
  --mixed_precision="fp16" ^
  --not_cache_latents ^
  --concepts_list="%CURPATH%data\datasets\example\concept.json" ^
  --use_8bit_adam ^
  --gradient_checkpointing ^
  --gradient_accumulation_steps=1 ^
  --learning_rate=2e-6 ^
  --lr_scheduler="constant" ^
  --lr_warmup_steps=0 ^
  --num_class_images=100 ^
  --sample_batch_size=4 ^
  --max_train_steps=100 ^
  --save_interval=50 ^
  --save_min_steps=50 ^
  --save_sample_prompt="Rick Roll"
  
  
cd ../../../../..
echo Training ended
pause