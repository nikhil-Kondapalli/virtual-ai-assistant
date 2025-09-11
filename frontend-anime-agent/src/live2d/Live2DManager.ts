export class Live2DManager {
  private canvas: HTMLCanvasElement | null = null;
  private ctx: CanvasRenderingContext2D | null = null;
  private container: HTMLElement | null = null;
  private isInitialized = false;
  private animationId: number | null = null;
  private isTalking = false;
  private talkAnimationFrame = 0;

  constructor() {
    // TBD
  }

  async initialize(container: HTMLElement): Promise<void> {
    if (this.isInitialized) return;

    this.container = container;

    try {
      // Create canvas element
      this.canvas = document.createElement("canvas");
      this.canvas.width = container.clientWidth;
      this.canvas.height = container.clientHeight;
      this.canvas.style.width = "100%";
      this.canvas.style.height = "100%";
      this.canvas.style.display = "block";

      // Get 2D context
      this.ctx = this.canvas.getContext("2d");
      if (!this.ctx) {
        throw new Error("Could not get 2D context from canvas");
      }

      // Add canvas to container
      container.appendChild(this.canvas);

      // Draw initial avatar
      this.drawAvatar();

      this.isInitialized = true;
      console.log("Live2D manager initialized with HTML5 Canvas avatar");
    } catch (error) {
      console.error("Error initializing Live2D manager:", error);
      throw error;
    }
  }

  private drawAvatar(): void {
    if (!this.ctx || !this.canvas) return;

    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;
    const radius = Math.min(this.canvas.width, this.canvas.height) * 0.15;

    // Clear canvas
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw head (light pink circle)
    this.ctx.beginPath();
    this.ctx.fillStyle = "#FFB6C1";
    this.ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    this.ctx.fill();

    // Draw eyes
    this.ctx.beginPath();
    this.ctx.fillStyle = "#000000";
    this.ctx.arc(
      centerX - radius * 0.3,
      centerY - radius * 0.25,
      radius * 0.1,
      0,
      2 * Math.PI
    );
    this.ctx.fill();

    this.ctx.beginPath();
    this.ctx.arc(
      centerX + radius * 0.3,
      centerY - radius * 0.25,
      radius * 0.1,
      0,
      2 * Math.PI
    );
    this.ctx.fill();

    // Draw mouth
    this.ctx.beginPath();
    this.ctx.fillStyle = "#FF69B4";
    this.ctx.ellipse(
      centerX,
      centerY + radius * 0.125,
      radius * 0.2,
      radius * 0.1,
      0,
      0,
      2 * Math.PI
    );
    this.ctx.fill();

    // Add some sparkle to the eyes
    this.ctx.beginPath();
    this.ctx.fillStyle = "#FFFFFF";
    this.ctx.arc(
      centerX - radius * 0.25,
      centerY - radius * 0.3,
      radius * 0.03,
      0,
      2 * Math.PI
    );
    this.ctx.fill();

    this.ctx.beginPath();
    this.ctx.arc(
      centerX + radius * 0.35,
      centerY - radius * 0.3,
      radius * 0.03,
      0,
      2 * Math.PI
    );
    this.ctx.fill();
  }

  private drawTalkingAvatar(): void {
    if (!this.ctx || !this.canvas) return;

    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;
    const radius = Math.min(this.canvas.width, this.canvas.height) * 0.15;

    // Clear canvas
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw head with slight scale variation for talking effect
    const scale = 1 + Math.sin(this.talkAnimationFrame * 0.3) * 0.05;
    this.ctx.save();
    this.ctx.translate(centerX, centerY);
    this.ctx.scale(scale, scale);
    this.ctx.translate(-centerX, -centerY);

    // Draw head (light pink circle)
    this.ctx.beginPath();
    this.ctx.fillStyle = "#FFB6C1";
    this.ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    this.ctx.fill();

    // Draw eyes
    this.ctx.beginPath();
    this.ctx.fillStyle = "#000000";
    this.ctx.arc(
      centerX - radius * 0.3,
      centerY - radius * 0.25,
      radius * 0.1,
      0,
      2 * Math.PI
    );
    this.ctx.fill();

    this.ctx.beginPath();
    this.ctx.arc(
      centerX + radius * 0.3,
      centerY - radius * 0.25,
      radius * 0.1,
      0,
      2 * Math.PI
    );
    this.ctx.fill();

    // Draw animated mouth (wider when talking)
    const mouthWidth =
      radius * 0.2 +
      Math.abs(Math.sin(this.talkAnimationFrame * 0.4)) * radius * 0.1;
    this.ctx.beginPath();
    this.ctx.fillStyle = "#FF69B4";
    this.ctx.ellipse(
      centerX,
      centerY + radius * 0.125,
      mouthWidth,
      radius * 0.1,
      0,
      0,
      2 * Math.PI
    );
    this.ctx.fill();

    // Add some sparkle to the eyes
    this.ctx.beginPath();
    this.ctx.fillStyle = "#FFFFFF";
    this.ctx.arc(
      centerX - radius * 0.25,
      centerY - radius * 0.3,
      radius * 0.03,
      0,
      2 * Math.PI
    );
    this.ctx.fill();

    this.ctx.beginPath();
    this.ctx.arc(
      centerX + radius * 0.35,
      centerY - radius * 0.3,
      radius * 0.03,
      0,
      2 * Math.PI
    );
    this.ctx.fill();

    this.ctx.restore();
  }

  private animateTalking = (): void => {
    if (!this.isTalking) return;

    this.talkAnimationFrame++;
    this.drawTalkingAvatar();
    this.animationId = requestAnimationFrame(this.animateTalking);
  };

  async loadModel(modelPath: string): Promise<void> {
    console.log(
      "Live2D model loading not implemented yet. Using HTML5 Canvas avatar."
    );
    // For now, just use the HTML5 Canvas avatar
    // In the future, this would load actual Live2D models
  }

  playAnimation(animationName: string): void {
    console.log(`Playing animation: ${animationName}`);

    // Simple animation effects
    switch (animationName) {
      case "smile":
        this.drawAvatar();
        // Add a brief scale effect
        setTimeout(() => {
          if (this.ctx && this.canvas) {
            this.ctx.save();
            this.ctx.scale(1.1, 1.1);
            this.ctx.translate(
              -this.canvas.width * 0.05,
              -this.canvas.height * 0.05
            );
            this.drawAvatar();
            this.ctx.restore();
            setTimeout(() => this.drawAvatar(), 500);
          }
        }, 0);
        break;
      case "happy":
        this.drawAvatar();
        // Add a brief rotation effect
        setTimeout(() => {
          if (this.ctx && this.canvas) {
            this.ctx.save();
            this.ctx.translate(this.canvas.width / 2, this.canvas.height / 2);
            this.ctx.rotate(0.1);
            this.ctx.translate(-this.canvas.width / 2, -this.canvas.height / 2);
            this.drawAvatar();
            this.ctx.restore();
            setTimeout(() => this.drawAvatar(), 300);
          }
        }, 0);
        break;
      case "sad":
        this.drawAvatar();
        // Add a brief scale down effect
        setTimeout(() => {
          if (this.ctx && this.canvas) {
            this.ctx.save();
            this.ctx.scale(0.9, 0.9);
            this.ctx.translate(
              this.canvas.width * 0.05,
              this.canvas.height * 0.05
            );
            this.drawAvatar();
            this.ctx.restore();
            setTimeout(() => this.drawAvatar(), 500);
          }
        }, 0);
        break;
      case "talking":
        this.startTalking();
        break;
      default:
        this.drawAvatar();
    }
  }

  setExpression(expressionName: string): void {
    console.log(`Setting expression: ${expressionName}`);
    this.playAnimation(expressionName);
  }

  startTalking(): void {
    console.log("Starting talking animation");
    this.isTalking = true;
    this.talkAnimationFrame = 0;
    this.animateTalking();
  }

  stopTalking(): void {
    console.log("Stopping talking animation");
    this.isTalking = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
    this.drawAvatar();
  }

  resize(width: number, height: number): void {
    if (!this.canvas) return;

    this.canvas.width = width;
    this.canvas.height = height;
    this.drawAvatar();
  }

  destroy(): void {
    this.isTalking = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }

    if (this.canvas && this.container) {
      this.container.removeChild(this.canvas);
    }

    this.canvas = null;
    this.ctx = null;
    this.isInitialized = false;
    console.log("Live2D manager destroyed");
  }

  getModel(): any {
    return this.canvas;
  }

  isReady(): boolean {
    return this.isInitialized && this.canvas !== null;
  }
}
